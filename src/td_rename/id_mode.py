"""Simple renaming mode that uses the folder id as the filename."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from .common import (
    copy_and_rename,
    ensure_unique_path,
    iter_file_folders,
    locate_single_file,
    sanitise_filename,
)


def rename_with_id(
    input_dir: Path,
    output_dir: Path,
    *,
    limit: Optional[int] = None,
) -> None:
    """Copy files while renaming them to their folder id."""

    if not input_dir.is_dir():
        raise FileNotFoundError(
            f"Input directory '{input_dir}' does not exist or is not a directory."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    folders: Iterable[Path] = iter_file_folders(input_dir)
    if limit is not None:
        folders = list(folders)[: max(limit, 0)]

    for folder in folders:
        source_file = locate_single_file(folder)
        if source_file is None:
            continue
        stem = sanitise_filename(folder.name)
        destination = ensure_unique_path(output_dir / f"{stem}.taf")
        copy_and_rename(source_file, destination)
