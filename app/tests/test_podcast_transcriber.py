import hashlib
from pathlib import Path

import pytest

from app.services.podcast_transcriber import (
    PodcastEpisode,
    PodcastError,
    PodcastTranscript,
    download_podcast_audio,
    extract_podcast_transcript,
    is_podcast_url,
    is_transcribable_podcast_url,
    resolve_podcast_audio_source,
    select_podcast_episodes,
    transcribe_podcast_episodes,
    transcribe_podcast_episodes_with_timeout,
)


def test_is_podcast_url_matches_known_domains_and_titles() -> None:
    assert is_podcast_url("https://open.spotify.com/episode/abc")
    assert is_podcast_url("https://podcasts.apple.com/us/podcast/show/id123")
    assert is_podcast_url("https://example.com/episode-1", "Podcast Episode 1")
    assert is_podcast_url("https://cdn.example.com/audio.mp3")
    assert is_podcast_url("https://example.com/article") is False


def test_is_transcribable_podcast_url_requires_supported_episode_sources() -> None:
    assert is_transcribable_podcast_url(
        "https://podcasts.apple.com/us/podcast/show/id123?i=1000744678894"
    )
    assert is_transcribable_podcast_url(
        "https://fundbuildscale.podbean.com/e/building-an-enterprise-ai-startup-from-day-zero/"
    )
    assert is_transcribable_podcast_url(
        "https://podscan.fm/podcasts/the-engineering-leadership-podcast/episodes/foo"
    )
    assert is_transcribable_podcast_url("https://pod.wave.co/podcast/show/episode")
    assert is_transcribable_podcast_url("https://plinkhq.com/i/1627920305/e/1000744678894")
    assert is_transcribable_podcast_url("https://cdn.example.com/audio.mp3")
    assert is_transcribable_podcast_url("https://open.spotify.com/episode/abc") is False
    assert is_transcribable_podcast_url("https://podcasts.apple.com/us/podcast/show/id123") is False


def test_select_podcast_episodes_resolves_audio_and_cleans_urls(monkeypatch) -> None:
    entries = [
        {
            "url": (
                "https://podcasts.apple.com/us/podcast/show/id123?i=1000744678894"
                "&quot;,&quot;text&quot;:&quot;Apple"
            ),
            "title": "Episode One",
        },
        {"url": "https://example.com/article", "title": "Restaurant review article"},
        {"url": "https://open.spotify.com/episode/abc", "title": "Blocked"},
        {
            "url": "https://podcasts.apple.com/us/podcast/show/id123?i=1000744678894",
            "title": "Duplicate",
        },
    ]

    def _resolve(url: str):
        if "apple.com" not in url:
            raise PodcastError("unsupported")
        return type(
            "Resolved",
            (),
            {
                "audio_url": "https://cdn.example.com/episode-one.mp3",
                "title": "Resolved Episode",
            },
        )()

    monkeypatch.setattr("app.services.podcast_transcriber.resolve_podcast_audio_source", _resolve)

    episodes = select_podcast_episodes(entries, max_episodes=3)

    assert episodes == [
        PodcastEpisode(
            url="https://podcasts.apple.com/us/podcast/show/id123?i=1000744678894",
            title="Episode One",
            audio_url="https://cdn.example.com/episode-one.mp3",
        )
    ]


def test_resolve_podcast_audio_source_finds_html_audio(monkeypatch) -> None:
    class _Response:
        def __init__(self, text: str, url: str) -> None:
            self.text = text
            self.url = url

        def raise_for_status(self) -> None:
            return

    monkeypatch.setattr(
        "app.services.podcast_transcriber.httpx.get",
        lambda *args, **kwargs: _Response(
            """
            <html>
              <head><title>Episode Example</title></head>
              <body>
                <script>var audio="https://cdn.example.com/podcast-episode.mp3";</script>
              </body>
            </html>
            """,
            "https://example.com/episode",
        ),
    )

    result = resolve_podcast_audio_source("https://example.com/episode")

    assert result.audio_url == "https://cdn.example.com/podcast-episode.mp3"
    assert result.title == "Episode Example"


def test_resolve_podcast_audio_source_uses_embedded_rss_url(monkeypatch) -> None:
    class _Response:
        def __init__(self, text: str, url: str) -> None:
            self.text = text
            self.url = url

        def raise_for_status(self) -> None:
            return

    def _get(url: str, *args, **kwargs):  # noqa: ANN002, ANN003
        if url == "https://example.com/episode":
            return _Response(
                """
                <html>
                  <head><title>Episode Example</title></head>
                  <body>
                    <script>window.__DATA__ = {"feed":"https://feeds.example.com/show.rss"};</script>
                  </body>
                </html>
                """,
                url,
            )
        if url == "https://feeds.example.com/show.rss":
            return _Response(
                """
                <rss>
                  <channel>
                    <item>
                      <title>Episode Example</title>
                      <enclosure
                        url="https://cdn.example.com/podcast-episode.mp3"
                        type="audio/mpeg"
                      />
                    </item>
                  </channel>
                </rss>
                """,
                url,
            )
        raise AssertionError(url)

    monkeypatch.setattr("app.services.podcast_transcriber.httpx.get", _get)

    result = resolve_podcast_audio_source("https://example.com/episode")

    assert result.audio_url == "https://cdn.example.com/podcast-episode.mp3"
    assert result.title == "Episode Example"


def test_resolve_podcast_audio_source_does_not_treat_wave_domain_as_audio(
    monkeypatch,
) -> None:
    class _Response:
        def __init__(self, text: str, url: str) -> None:
            self.text = text
            self.url = url

        def raise_for_status(self) -> None:
            return

    monkeypatch.setattr(
        "app.services.podcast_transcriber.httpx.get",
        lambda *args, **kwargs: _Response(
            "<html><head><title>Pod Wave</title></head><body>No audio here.</body></html>",
            "https://pod.wave.co/podcast/show/episode",
        ),
    )

    with pytest.raises(PodcastError, match="supported episode or direct audio source"):
        resolve_podcast_audio_source("https://pod.wave.co/podcast/show/episode")


def test_download_podcast_audio_reuses_existing_file(tmp_path: Path, monkeypatch) -> None:
    audio_url = "https://cdn.example.com/podcast-episode.mp3"
    digest = hashlib.sha1(audio_url.encode("utf-8")).hexdigest()[:12]
    audio_path = tmp_path / f"{digest}-episode-example.mp3"
    audio_path.write_bytes(b"audio")

    monkeypatch.setattr(
        "app.services.podcast_transcriber.resolve_podcast_audio_source",
        lambda _url: type(
            "Resolved",
            (),
            {
                "audio_url": audio_url,
                "title": "Episode Example",
            },
        )(),
    )

    result_path, title = download_podcast_audio("https://example.com/episode", tmp_path)

    assert result_path == audio_path
    assert title == "Episode Example"


def test_extract_podcast_transcript_uses_local_whisper(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.podcast_transcriber.download_podcast_audio",
        lambda *_args, **_kwargs: (tmp_path / "audio" / "episode-1.mp3", "Episode 1"),
    )
    monkeypatch.setattr(
        "app.services.podcast_transcriber.transcribe_local_audio",
        lambda *_args, **_kwargs: "Transcript text",
    )

    transcript_id, title, transcript = extract_podcast_transcript(
        PodcastEpisode(url="https://open.spotify.com/episode/abc"),
        tmp_path / "audio",
        tmp_path / "transcripts",
        "base",
    )

    assert transcript_id == "episode-1"
    assert title == "Episode 1"
    assert transcript == "Transcript text"


def test_transcribe_podcast_episodes_skips_failed_episode(tmp_path: Path, monkeypatch) -> None:
    episodes = [
        PodcastEpisode(url="https://open.spotify.com/episode/bad", title="Bad"),
        PodcastEpisode(url="https://open.spotify.com/episode/good", title="Good"),
    ]

    def _extract(episode: PodcastEpisode, *_args, **_kwargs):
        if episode.url.endswith("/bad"):
            raise PodcastError("blocked")
        return "good", "Recovered", "Transcript text"

    monkeypatch.setattr("app.services.podcast_transcriber.extract_podcast_transcript", _extract)

    transcripts = transcribe_podcast_episodes(
        episodes=episodes,
        audio_dir=tmp_path / "audio",
        transcript_dir=tmp_path / "transcripts",
        model_name="base",
    )

    assert transcripts == [
        PodcastTranscript(
            url="https://open.spotify.com/episode/good",
            title="Good",
            transcript="Transcript text",
        )
    ]
    assert (tmp_path / "transcripts" / "good.txt").exists()


def test_transcribe_podcast_episodes_with_timeout_terminates_worker(
    tmp_path: Path, monkeypatch
) -> None:
    class FakeQueue:
        def close(self) -> None:
            return

        def get_nowait(self):  # noqa: ANN201
            raise AssertionError("timed out worker should not return a payload")

    class FakeProcess:
        def __init__(self) -> None:
            self.started = False
            self.terminated = False
            self.killed = False

        def start(self) -> None:
            self.started = True

        def join(self, timeout=None) -> None:  # noqa: ANN001
            return

        def is_alive(self) -> bool:
            return not self.terminated and not self.killed

        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            self.killed = True

    fake_process = FakeProcess()

    class FakeContext:
        def Queue(self, maxsize=1):  # noqa: N802, ANN001, ANN201
            return FakeQueue()

        def Process(self, target, args):  # noqa: N802, ANN001, ANN201
            del target, args
            return fake_process

    monkeypatch.setattr(
        "app.services.podcast_transcriber.multiprocessing.get_context",
        lambda method: FakeContext(),
    )

    with pytest.raises(TimeoutError, match="timed out"):
        transcribe_podcast_episodes_with_timeout(
            episodes=[PodcastEpisode(url="https://open.spotify.com/episode/abc", title="Episode")],
            audio_dir=tmp_path / "audio",
            transcript_dir=tmp_path / "transcripts",
            model_name="base",
            timeout_seconds=5,
        )

    assert fake_process.started is True
    assert fake_process.terminated is True
