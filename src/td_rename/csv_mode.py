"""Renaming logic that uses a CSV metadata mapping."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from .common import (
    copy_and_rename,
    ensure_unique_path,
    iter_file_folders,
    locate_single_file,
    sanitise_filename,
)


@dataclass(frozen=True)
class Metadata:
    """Metadata describing the series and episode names."""

    series: Optional[str]
    episode: Optional[str]

    def has_information(self) -> bool:
        """Return ``True`` when at least one metadata field is populated."""

        return bool(self.series or self.episode)

    def build_filename(self) -> str:
        """Generate a filename stem from the metadata."""

        parts = []
        if self.series:
            parts.append(self.series.strip())
        if self.episode:
            episode = self.episode.strip()
            if episode:
                parts.append(episode)

        return " - ".join(parts)


def load_metadata(csv_path: Path) -> Dict[str, Metadata]:
    """Load the metadata mapping from the CSV file."""

    mapping: Dict[str, Metadata] = {}
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            file_id = (row.get("Name") or "").strip()
            if not file_id:
                continue
            series = (row.get("Series") or "").strip() or None
            episode = (row.get("Episode") or "").strip() or None
            mapping[file_id.upper()] = Metadata(series=series, episode=episode)
    return mapping


def _process_folder(
    folder: Path,
    metadata: Dict[str, Metadata],
    output_dir: Path,
    unmatched_dir: Path,
) -> None:
    file_id = folder.name
    source_file = locate_single_file(folder)
    if source_file is None:
        return

    meta = metadata.get(file_id.upper())
    if meta and meta.has_information():
        stem = sanitise_filename(meta.build_filename())
        destination = ensure_unique_path(output_dir / f"{stem}.taf")
    else:
        stem = sanitise_filename(file_id)
        destination = ensure_unique_path(unmatched_dir / f"{stem}.taf")

    copy_and_rename(source_file, destination)


def rename_from_csv(
    input_dir: Path,
    csv_file: Path,
    output_dir: Path,
    *,
    limit: Optional[int] = None,
) -> None:
    """Rename files using the CSV metadata."""

    if not input_dir.is_dir():
        raise FileNotFoundError(
            f"Input directory '{input_dir}' does not exist or is not a directory."
        )
    if not csv_file.is_file():
        raise FileNotFoundError(f"CSV file '{csv_file}' does not exist or is not a file.")

    metadata = load_metadata(csv_file)
    unmatched_dir = output_dir / "unmatched"
    output_dir.mkdir(parents=True, exist_ok=True)

    folders: Iterable[Path] = iter_file_folders(input_dir)
    if limit is not None:
        folders = list(folders)[: max(limit, 0)]
    for folder in folders:
        _process_folder(folder, metadata, output_dir, unmatched_dir)
