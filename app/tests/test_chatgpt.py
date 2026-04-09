from app.services.chatgpt import build_chatgpt_continue_url


def test_build_chatgpt_continue_url_embeds_summary_text() -> None:
    url = build_chatgpt_continue_url("Best office chair\n\nStrong lumbar support.")

    assert url.startswith("https://chatgpt.com/?query=")
    assert "Continue%20this%20conversation%20based%20on%20the%20summary%20below" in url
    assert "Best%20office%20chair" in url
    assert "Strong%20lumbar%20support." in url


def test_build_chatgpt_continue_url_clips_very_long_summaries() -> None:
    url = build_chatgpt_continue_url("x" * 3000)

    assert url.startswith("https://chatgpt.com/?query=")
    assert len(url) < 2400
