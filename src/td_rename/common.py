"""Shared helpers used by the td_rename package."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, Optional


def iter_file_folders(path: Path) -> Iterable[Path]:
    """Yield immediate subdirectories that contain at least one file."""

    for child in sorted(path.iterdir()):
        if child.is_dir():
            yield child


def locate_single_file(folder: Path) -> Optional[Path]:
    """Return the first file found inside ``folder`` or ``None`` if missing."""

    for child in folder.iterdir():
        if child.is_file():
            return child
    return None


def sanitise_filename(name: str) -> str:
    """Remove characters that are problematic on common filesystems."""

    forbidden = {"/", "\0", "\n", "\r", "\t"}
    sanitized = "".join("_" if ch in forbidden else ch for ch in name)
    return sanitized.strip() or "unnamed"


def ensure_unique_path(target: Path) -> Path:
    """Return a unique path by appending a numeric suffix when needed."""

    if not target.exists():
        return target

    counter = 1
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def copy_and_rename(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
