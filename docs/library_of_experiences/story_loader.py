"""Load original experiment stories from YAML without changing their contents."""

from pathlib import Path
import yaml

_STORY_DIR = Path(__file__).resolve().parent


def _read_stories(filename):
    with (_STORY_DIR / filename).open(encoding="utf-8") as story_file:
        return yaml.safe_load(story_file)


def load_query_stories():
    return [(story["title"], story["text"]) for story in _read_stories("query_stories.yaml")]


def load_candidate_stories():
    return {story["title"]: story["text"] for story in _read_stories("candidate_stories.yaml")}
