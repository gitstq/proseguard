"""Configuration loading and validation.

Config resolution order (later wins): built-in defaults → ``.proseguard.json``
found by walking up from the target file's directory → explicit ``--config``
file → CLI flags.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILENAME = ".proseguard.json"
DEFAULT_EXTENSIONS = (".md", ".markdown", ".txt", ".rst", ".tex")
DEFAULT_EXCLUDES = (
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "dist",
    "build", "__pycache__", ".tox", ".mypy_cache",
)


@dataclass
class Config:
    enable: set[str] = field(default_factory=set)      # empty = all enabled
    disable: set[str] = field(default_factory=set)
    max_sentence_words: int = 25
    long_sentence_hard: int = 40
    readability_grade: float = 12.0
    personal_dictionary: set[str] = field(default_factory=set)
    extensions: set[str] = field(default_factory=lambda: set(DEFAULT_EXTENSIONS))
    excludes: set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDES))
    config_path: str | None = None

    def is_enabled(self, rule_id: str) -> bool:
        if rule_id in self.disable:
            return False
        if self.enable and rule_id not in self.enable:
            return False
        return True

    def merge_file(self, path: Path) -> "Config":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{path}: top-level config must be a JSON object")
        self.enable |= {str(x).upper() for x in data.get("enable", [])}
        self.disable |= {str(x).upper() for x in data.get("disable", [])}
        for key in ("max_sentence_words", "long_sentence_hard"):
            if key in data:
                setattr(self, key, int(data[key]))
        if "readability_grade" in data:
            self.readability_grade = float(data["readability_grade"])
        self.personal_dictionary |= {
            str(w).lower() for w in data.get("personal_dictionary", [])
        }
        if "extensions" in data:
            self.extensions = {
                e if e.startswith(".") else f".{e}" for e in data["extensions"]
            }
        if "excludes" in data:
            self.excludes |= set(data["excludes"])
        return self


def find_config(start: Path | None = None) -> Path | None:
    cur = (start or Path.cwd()).resolve()
    for directory in (cur, *cur.parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_config(explicit: str | Path | None = None,
                search_from: Path | None = None) -> Config:
    cfg = Config()
    path: Path | None
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise FileNotFoundError(f"config file not found: {path}")
    else:
        path = find_config(search_from)
    if path is not None:
        cfg.config_path = str(path)
        cfg.merge_file(path)
    return cfg
