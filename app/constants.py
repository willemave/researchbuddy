"""Application constants."""

from pathlib import Path

APP_NAME = "ResearchBuddy"
APP_VERSION = "0.1.4"
DEFAULT_DATA_DIR = Path("./data")
DEFAULT_STORAGE_DIR = DEFAULT_DATA_DIR / "storage"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "researchbuddy.db"

URL_STATUS_PENDING = "pending"
URL_STATUS_FETCHED = "fetched"
URL_STATUS_FAILED = "failed"

RUN_STATUS_IN_PROGRESS = "in_progress"
RUN_STATUS_COMPLETED = "completed"
RUN_STATUS_FAILED = "failed"

FOLLOWUP_MEMORY_FILENAME = "followup_memory.json"
YOUTUBE_TRANSCRIPTS_FILENAME = "youtube_transcripts.json"
PODCAST_TRANSCRIPTS_FILENAME = "podcast_transcripts.json"
