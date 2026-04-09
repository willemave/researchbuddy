"""Podcast ingestion and Whisper transcription helpers."""

from __future__ import annotations

import hashlib
import html
import logging
import multiprocessing
import queue
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx
from pydantic import BaseModel

from app.services.local_audio_transcriber import transcribe_audio as transcribe_local_audio

logger = logging.getLogger(__name__)

PODCAST_DOMAINS = (
    "podcasts.apple.com",
    "open.spotify.com",
    "overcast.fm",
    "pca.st",
    "podbean.com",
    "buzzsprout.com",
    "simplecast.com",
    "libsyn.com",
    "megaphone.fm",
    "acast.com",
    "transistor.fm",
    "captivate.fm",
    "plinkhq.com",
    "podscan.fm",
)
TRANSCRIBABLE_PODCAST_HOSTS = (
    "podcasts.apple.com",
    "pod.wave.co",
    "podscan.fm",
    "plinkhq.com",
    "buzzsprout.com",
    "podbean.com",
    "simplecast.com",
    "libsyn.com",
    "megaphone.fm",
    "acast.com",
    "transistor.fm",
    "captivate.fm",
    "fireside.fm",
)
PODCAST_MARKERS = (
    "episode",
    "interview",
    "show notes",
    "podcast",
)
PODCAST_AUDIO_SUFFIXES = (".mp3", ".m4a", ".aac", ".wav", ".ogg")
PODCAST_EPISODE_PATH_MARKERS = ("/episode/", "/episodes/", "/ep/", "/e/")
APPLE_PODCAST_ID_REGEX = re.compile(r"/id(?P<podcast_id>\d+)")
AUDIO_URL_PATTERN = re.compile(
    r"""https?://[^\s"'<>]+?\.(?:mp3|m4a|aac|wav|ogg)(?:\?[^\s"'<>]*)?""",
    re.IGNORECASE,
)
RSS_LINK_PATTERN = re.compile(
    r"""<link[^>]+type=["']application/(?:rss|atom)\+xml["'][^>]+href=["']([^"']+)["']""",
    re.IGNORECASE,
)
RSS_URL_PATTERN = re.compile(r"""https?://[^\s"'<>]+?\.rss(?:\?[^\s"'<>]*)?""", re.IGNORECASE)
META_TITLE_PATTERN = re.compile(
    r"""<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)["']""",
    re.IGNORECASE,
)
TITLE_TAG_PATTERN = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
STOPWORDS = {"the", "and", "of", "a", "an", "to", "in", "on", "for", "with"}
HTTP_TIMEOUT = httpx.Timeout(45.0, connect=15.0, read=45.0, write=30.0, pool=10.0)
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; researchbuddy/1.0; Podcast Downloader)",
}


class PodcastError(RuntimeError):
    """Raised when podcast ingestion fails."""


class PodcastEpisode(BaseModel):
    """Podcast episode metadata."""

    url: str
    title: str | None = None
    audio_url: str | None = None


class PodcastTranscript(BaseModel):
    """Podcast transcript with metadata."""

    url: str
    title: str | None = None
    transcript: str


@dataclass(frozen=True)
class PodcastAudioSource:
    """Resolved podcast audio source."""

    audio_url: str
    title: str | None = None


def is_podcast_url(url: str, title: str | None = None) -> bool:
    """Return True when a URL or title looks podcast-like."""

    host = urlparse(url).netloc.lower()
    if any(host.endswith(domain) for domain in PODCAST_DOMAINS):
        return True
    if _is_direct_audio_url(url):
        return True
    lowered_title = (title or "").lower()
    return any(marker in lowered_title for marker in PODCAST_MARKERS)


def is_transcribable_podcast_url(url: str) -> bool:
    """Return True when the URL looks like a transcribable podcast episode."""

    if _is_direct_audio_url(url):
        return True

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if host.endswith("podcasts.apple.com"):
        return _extract_apple_episode_id(url) is not None
    if host.endswith("pod.wave.co"):
        return path.startswith("/podcast/") and path.count("/") >= 3

    if not any(host.endswith(domain) for domain in TRANSCRIBABLE_PODCAST_HOSTS):
        return False

    return any(marker in path for marker in PODCAST_EPISODE_PATH_MARKERS)


def select_podcast_episodes(entries: Iterable[object], max_episodes: int) -> list[PodcastEpisode]:
    """Select resolvable podcast episodes from search results."""

    if max_episodes <= 0:
        return []

    candidates: list[PodcastEpisode] = []
    seen_urls: set[str] = set()
    for entry in entries:
        raw_url, title = _entry_fields(entry)
        url = _normalize_candidate_url(raw_url)
        if not url or url in seen_urls or not is_podcast_url(url, title):
            continue
        seen_urls.add(url)
        candidates.append(PodcastEpisode(url=url, title=title))

    if not candidates:
        return []

    episodes: list[PodcastEpisode] = []
    seen_audio_urls: set[str] = set()
    probe_limit = min(len(candidates), max(max_episodes * 4, max_episodes))
    for candidate in candidates[:probe_limit]:
        try:
            resolved = resolve_podcast_audio_source(candidate.url)
        except PodcastError:
            continue
        if resolved.audio_url in seen_audio_urls:
            continue
        seen_audio_urls.add(resolved.audio_url)
        episodes.append(
            PodcastEpisode(
                url=candidate.url,
                title=candidate.title or resolved.title,
                audio_url=resolved.audio_url,
            )
        )
        if len(episodes) >= max_episodes:
            break
    return episodes


def download_podcast_audio(
    episode_url: str,
    output_dir: Path,
    *,
    audio_url: str | None = None,
    title: str | None = None,
) -> tuple[Path, str | None]:
    """Download podcast audio locally."""

    output_dir.mkdir(parents=True, exist_ok=True)
    resolved = (
        PodcastAudioSource(audio_url=audio_url, title=title)
        if audio_url
        else resolve_podcast_audio_source(episode_url)
    )
    audio_path = _download_audio_file(resolved.audio_url, output_dir, resolved.title)
    return audio_path, resolved.title


def extract_podcast_transcript(
    episode: PodcastEpisode,
    audio_dir: Path,
    transcript_dir: Path,
    model_name: str,
) -> tuple[str, str | None, str]:
    """Download and transcribe a single podcast episode."""

    del transcript_dir
    audio_path, title = download_podcast_audio(
        episode.url,
        audio_dir,
        audio_url=episode.audio_url,
        title=episode.title,
    )
    transcript_text = transcribe_local_audio(audio_path, model_name, error_cls=PodcastError)
    return audio_path.stem, title, transcript_text


def transcribe_podcast_episodes(
    episodes: list[PodcastEpisode],
    audio_dir: Path,
    transcript_dir: Path,
    model_name: str,
) -> list[PodcastTranscript]:
    """Download and transcribe multiple podcast episodes."""

    if not episodes:
        return []

    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcripts: list[PodcastTranscript] = []
    for episode in episodes:
        try:
            transcript_id, resolved_title, transcript_text = extract_podcast_transcript(
                episode,
                audio_dir,
                transcript_dir,
                model_name,
            )
        except PodcastError as exc:
            logger.warning("Skipping podcast episode %s: %s", episode.url, exc)
            continue

        transcript_path = transcript_dir / f"{transcript_id}.txt"
        transcript_path.write_text(transcript_text, encoding="utf-8")
        transcripts.append(
            PodcastTranscript(
                url=episode.url,
                title=episode.title or resolved_title,
                transcript=transcript_text,
            )
        )
    return transcripts


def _transcribe_podcast_episodes_worker(
    episodes: list[dict],
    audio_dir: Path,
    transcript_dir: Path,
    model_name: str,
    result_queue,
) -> None:
    """Run podcast transcription work inside a child process."""

    try:
        transcripts = transcribe_podcast_episodes(
            episodes=[PodcastEpisode.model_validate(item) for item in episodes],
            audio_dir=audio_dir,
            transcript_dir=transcript_dir,
            model_name=model_name,
        )
    except Exception as exc:  # noqa: BLE001
        result_queue.put({"status": "error", "error": str(exc)})
        return

    result_queue.put(
        {
            "status": "ok",
            "transcripts": [item.model_dump() for item in transcripts],
        }
    )


def transcribe_podcast_episodes_with_timeout(
    episodes: list[PodcastEpisode],
    audio_dir: Path,
    transcript_dir: Path,
    model_name: str,
    timeout_seconds: int | float | None,
) -> list[PodcastTranscript]:
    """Run podcast transcription in a killable child process."""

    if timeout_seconds is None or timeout_seconds <= 0:
        return transcribe_podcast_episodes(
            episodes=episodes,
            audio_dir=audio_dir,
            transcript_dir=transcript_dir,
            model_name=model_name,
        )

    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_transcribe_podcast_episodes_worker,
        args=(
            [item.model_dump() for item in episodes],
            audio_dir,
            transcript_dir,
            model_name,
            result_queue,
        ),
    )

    try:
        process.start()
        process.join(timeout_seconds)
        if process.is_alive():
            process.terminate()
            process.join()
            if process.is_alive():
                process.kill()
                process.join()
            raise TimeoutError(f"Podcast ingestion timed out after {timeout_seconds} seconds")

        try:
            payload = result_queue.get_nowait()
        except queue.Empty as exc:
            raise PodcastError(
                "Podcast transcription worker exited without returning results"
            ) from exc

        if not isinstance(payload, dict):
            raise PodcastError("Podcast transcription worker returned an invalid payload")
        if payload.get("status") == "error":
            raise PodcastError(str(payload.get("error") or "Unknown podcast worker error"))
        if payload.get("status") != "ok":
            raise PodcastError("Podcast transcription worker returned an unknown status")

        transcripts = payload.get("transcripts", [])
        if not isinstance(transcripts, list):
            raise PodcastError("Podcast transcription worker returned invalid transcripts")
        return [PodcastTranscript.model_validate(item) for item in transcripts]
    finally:
        if hasattr(result_queue, "close"):
            result_queue.close()


def resolve_podcast_audio_source(episode_url: str) -> PodcastAudioSource:
    """Resolve a podcast episode page or audio URL to a direct audio source."""

    if _is_direct_audio_url(episode_url):
        return PodcastAudioSource(audio_url=episode_url, title=_title_from_url(episode_url))

    apple_resolution = _resolve_apple_podcast_episode(episode_url)
    if apple_resolution is not None:
        return apple_resolution

    html_resolution = _resolve_audio_from_html_page(episode_url)
    if html_resolution is not None:
        return html_resolution

    raise PodcastError("Podcast URL is not a supported episode or direct audio source")


def _resolve_apple_podcast_episode(url: str) -> PodcastAudioSource | None:
    show_id = _extract_apple_show_id(url)
    episode_id = _extract_apple_episode_id(url)
    if not show_id or not episode_id:
        return None

    lookup_url = (
        "https://itunes.apple.com/lookup"
        f"?id={show_id}&entity=podcastEpisode&limit=200"
    )
    try:
        response = httpx.get(lookup_url, timeout=HTTP_TIMEOUT, headers=HTTP_HEADERS)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise PodcastError(f"Apple Podcasts lookup failed: {exc}") from exc

    feed_url = None
    episode_title = None
    for item in payload.get("results", []):
        if not isinstance(item, dict):
            continue
        if feed_url is None and item.get("kind") == "podcast":
            feed_url = _as_optional_str(item.get("feedUrl"))
        if item.get("kind") == "podcast-episode" and str(item.get("trackId")) == episode_id:
            episode_title = _as_optional_str(item.get("trackName"))

    if not feed_url or not episode_title:
        raise PodcastError("Apple Podcasts URL did not resolve to an RSS episode")

    audio_url = _resolve_audio_url_from_rss(feed_url, episode_title)
    if audio_url is None:
        raise PodcastError("Apple Podcasts RSS feed did not expose an audio enclosure")

    return PodcastAudioSource(audio_url=audio_url, title=episode_title)


def _resolve_audio_from_html_page(url: str) -> PodcastAudioSource | None:
    try:
        response = httpx.get(url, follow_redirects=True, timeout=HTTP_TIMEOUT, headers=HTTP_HEADERS)
        response.raise_for_status()
    except Exception as exc:
        raise PodcastError(f"Podcast page fetch failed: {exc}") from exc

    page_url = str(response.url)
    body = response.text
    title = _extract_html_title(body)

    rss_url = _extract_rss_url_from_html(body, page_url)
    if rss_url and title:
        audio_url = _resolve_audio_url_from_rss(rss_url, title)
        if audio_url is not None:
            return PodcastAudioSource(audio_url=audio_url, title=title)

    audio_url = _extract_audio_url_from_html(body, page_url)
    if audio_url is not None:
        return PodcastAudioSource(audio_url=audio_url, title=title)

    return None


def _resolve_audio_url_from_rss(feed_url: str, episode_title: str) -> str | None:
    try:
        response = httpx.get(feed_url, timeout=HTTP_TIMEOUT, headers=HTTP_HEADERS)
        response.raise_for_status()
    except Exception:
        return None

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        return None

    best_audio_url = None
    best_score = 0
    target_tokens = _tokenize_title(episode_title)
    for item in root.findall(".//item"):
        item_title = _find_child_text(item, "title")
        if not item_title:
            continue
        audio_url = _extract_audio_url_from_rss_item(item)
        if not audio_url:
            continue
        if _normalize_title(item_title) == _normalize_title(episode_title):
            return audio_url

        item_tokens = _tokenize_title(item_title)
        score = len(set(item_tokens) & set(target_tokens))
        if score > best_score:
            best_score = score
            best_audio_url = audio_url

    min_score = max(3, len(target_tokens) // 2) if target_tokens else 0
    if best_score < min_score:
        return None
    return best_audio_url


def _extract_audio_url_from_rss_item(item: ET.Element) -> str | None:
    for child in item:
        local_name = _local_name(child.tag)
        if local_name != "enclosure":
            continue
        href = child.attrib.get("url") or child.attrib.get("href")
        media_type = child.attrib.get("type", "")
        if href and ("audio" in media_type.lower() or _is_direct_audio_url(href)):
            return html.unescape(href)

    for child in item:
        if _local_name(child.tag) != "link":
            continue
        href = (child.text or "").strip()
        media_type = child.attrib.get("type", "")
        if href and ("audio" in media_type.lower() or _is_direct_audio_url(href)):
            return html.unescape(href)

    return None


def _download_audio_file(audio_url: str, output_dir: Path, title: str | None) -> Path:
    filename_stem = _sanitize_filename(title or _title_from_url(audio_url) or "podcast-audio")
    suffix = _audio_suffix_from_url(audio_url)
    digest = hashlib.sha1(audio_url.encode("utf-8")).hexdigest()[:12]
    target_path = output_dir / f"{digest}-{filename_stem}{suffix}"
    temp_path = target_path.with_suffix(f"{target_path.suffix}.part")

    if target_path.exists() and target_path.stat().st_size > 0:
        return target_path

    temp_path.unlink(missing_ok=True)

    try:
        with httpx.stream(
            "GET",
            audio_url,
            follow_redirects=True,
            timeout=HTTP_TIMEOUT,
            headers=HTTP_HEADERS,
        ) as response:
            response.raise_for_status()
            output_dir.mkdir(parents=True, exist_ok=True)
            bytes_written = 0
            with temp_path.open("wb") as handle:
                for chunk in response.iter_bytes(chunk_size=8192):
                    if not chunk:
                        continue
                    handle.write(chunk)
                    bytes_written += len(chunk)
    except Exception as exc:
        temp_path.unlink(missing_ok=True)
        raise PodcastError(f"Podcast download failed: {exc}") from exc

    if bytes_written <= 0:
        temp_path.unlink(missing_ok=True)
        raise PodcastError("Podcast download produced an empty audio file")

    temp_path.replace(target_path)
    return target_path


def _extract_audio_url_from_html(body: str, page_url: str) -> str | None:
    normalized = (
        html.unescape(body)
        .replace("\\/", "/")
        .replace("\\u002F", "/")
        .replace("\\u0026", "&")
    )
    for candidate in _iter_audio_url_candidates(normalized, page_url):
        if candidate:
            return candidate

    for attribute in ("src", "href", "content"):
        pattern = re.compile(
            rf"""{attribute}=["']([^"']+?\.(?:mp3|m4a|aac|wav|ogg)(?:\?[^"']*)?)["']""",
            re.IGNORECASE,
        )
        match = pattern.search(normalized)
        if match:
            candidate = _decode_embedded_audio_url(urljoin(page_url, match.group(1)))
            if _is_direct_audio_url(candidate):
                return candidate

    return None


def _iter_audio_url_candidates(body: str, page_url: str) -> Iterable[str]:
    for match in AUDIO_URL_PATTERN.finditer(body):
        candidate = _decode_embedded_audio_url(urljoin(page_url, match.group(0)))
        if _is_direct_audio_url(candidate):
            yield candidate

    encoded_pattern = re.compile(
        r"""https?%3A%2F%2F[^"'<>\\\s]+?\.(?:mp3|m4a|aac|wav|ogg)(?:%3F[^"'<>\\\s]*)?""",
        re.IGNORECASE,
    )
    for match in encoded_pattern.finditer(body):
        candidate = _decode_embedded_audio_url(unquote(match.group(0)))
        if _is_direct_audio_url(candidate):
            yield candidate


def _extract_rss_url_from_html(body: str, page_url: str) -> str | None:
    match = RSS_LINK_PATTERN.search(body)
    if match:
        return urljoin(page_url, html.unescape(match.group(1)))

    normalized = html.unescape(body)
    match = RSS_URL_PATTERN.search(normalized)
    if not match:
        return None
    return urljoin(page_url, match.group(0))


def _extract_html_title(body: str) -> str | None:
    meta_match = META_TITLE_PATTERN.search(body)
    if meta_match:
        return html.unescape(meta_match.group(1)).strip() or None
    title_match = TITLE_TAG_PATTERN.search(body)
    if not title_match:
        return None
    title = re.sub(r"\s+", " ", html.unescape(title_match.group(1))).strip()
    return title or None


def _entry_fields(entry: object) -> tuple[str | None, str | None]:
    if isinstance(entry, dict):
        url = entry.get("url") or entry.get("link")
        title = entry.get("title")
        return _as_optional_str(url), _as_optional_str(title)

    url = getattr(entry, "url", None) or getattr(entry, "link", None)
    title = getattr(entry, "title", None)
    return _as_optional_str(url), _as_optional_str(title)


def _normalize_candidate_url(url: str | None) -> str | None:
    if not url:
        return None
    cleaned = html.unescape(url).strip()
    match = re.match(r"https?://[^\s\"'<>]+", cleaned)
    if not match:
        return None
    normalized = match.group(0).rstrip("),.;")
    return normalized or None


def _as_optional_str(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            return stripped
    return None


def _is_direct_audio_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(suffix) for suffix in PODCAST_AUDIO_SUFFIXES)


def _decode_embedded_audio_url(url: str) -> str:
    decoded = url
    for _ in range(3):
        if "https%3A%2F%2F" not in decoded and "http%3A%2F%2F" not in decoded:
            break
        decoded = unquote(decoded)
    return decoded


def _audio_suffix_from_url(url: str) -> str:
    lowered = urlparse(url).path.lower()
    for suffix in PODCAST_AUDIO_SUFFIXES:
        if lowered.endswith(suffix):
            return suffix
    return ".mp3"


def _extract_apple_show_id(url: str) -> str | None:
    match = APPLE_PODCAST_ID_REGEX.search(urlparse(url).path)
    if not match:
        return None
    return match.group("podcast_id")


def _extract_apple_episode_id(url: str) -> str | None:
    episode_id = parse_qs(urlparse(url).query).get("i", [None])[0]
    if isinstance(episode_id, str) and episode_id.isdigit():
        return episode_id
    return None


def _local_name(value: str) -> str:
    if "}" in value:
        return value.rsplit("}", 1)[1]
    return value


def _find_child_text(item: ET.Element, name: str) -> str | None:
    for child in item:
        if _local_name(child.tag) != name:
            continue
        text = (child.text or "").strip()
        if text:
            return text
    return None


def _normalize_title(title: str) -> str:
    return " ".join(_tokenize_title(title))


def _tokenize_title(title: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", title.lower())
    return [token for token in tokens if token not in STOPWORDS]


def _title_from_url(url: str) -> str | None:
    stem = Path(urlparse(url).path).stem
    title = stem.replace("-", " ").replace("_", " ").strip()
    return title or None


def _sanitize_filename(value: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", value).strip().lower()
    normalized = re.sub(r"[-\s]+", "-", normalized)
    return normalized[:100] or "podcast-audio"
