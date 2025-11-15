#!/usr/bin/env python3
"""Rename Toniebox files based on a CSV mapping.

The script expects three positional arguments:

1. The input directory that contains subfolders. Each subfolder holds a
   single file whose enclosing directory name is treated as the *file id*.
2. A CSV file that maps the file id to the *Series* and *Episode* metadata.
3. An output directory. The renamed files are copied into this directory.

The resulting output directory is flat: every renamed file – regardless of the
original directory structure – ends up in the same folder. Files that cannot be
matched to metadata are copied into ``<output>/unmatched`` and renamed to their
file id. All produced files use the ``.taf`` extension.

Use ``--test N`` to limit the execution to the first *N* folders. This is
useful for a dry run with a couple of samples.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class Metadata:
    """Metadata describing the series and episode names."""

    series: Optional[str]
    episode: Optional[str]

    def has_information(self) -> bool:
        """Return ``True`` when at least one metadata field is populated."""

        return bool(self.series or self.episode)

    def build_filename(self) -> str:
        """Generate a filename stem from the metadata.

        When both *series* and *episode* are available we join them with
        ``" - "``. When only one of them is present we fall back to the value
        that exists. The caller is responsible for appending the ``.taf``
        extension and handling duplicates.
        """

        parts = []
        if self.series:
            parts.append(self.series.strip())
        if self.episode:
            episode = self.episode.strip()
            if episode:
                parts.append(episode)

        # ``parts`` is guaranteed to contain at least one entry because the
        # caller checks ``has_information`` before invoking ``build_filename``.
        return " - ".join(parts)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing folders whose names represent file ids.",
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="CSV file with the columns 'Name', 'Series', 'Episode'.",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Destination directory that will receive the renamed files.",
    )
    parser.add_argument(
        "--test",
        type=int,
        metavar="N",
        default=None,
        help=(
            "Only process the first N folders. Useful for quickly testing the "
            "workflow on a couple of samples."
        ),
    )
    return parser.parse_args()


def load_metadata(csv_path: Path) -> Dict[str, Metadata]:
    """Load the metadata mapping from the CSV file.

    Keys are upper-case file ids to allow case-insensitive lookups.
    """

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


def process_folder(
    folder: Path,
    metadata: Dict[str, Metadata],
    output_dir: Path,
    unmatched_dir: Path,
) -> None:
    file_id = folder.name
    source_file = locate_single_file(folder)
    if source_file is None:
        # Nothing to copy; skip silently.
        return

    meta = metadata.get(file_id.upper())
    if meta and meta.has_information():
        stem = sanitise_filename(meta.build_filename())
        destination = ensure_unique_path(output_dir / f"{stem}.taf")
    else:
        stem = sanitise_filename(file_id)
        destination = ensure_unique_path(unmatched_dir / f"{stem}.taf")

    copy_and_rename(source_file, destination)


def main() -> None:
    args = parse_arguments()

    if not args.input_dir.is_dir():
        raise SystemExit(f"Input directory '{args.input_dir}' does not exist or is not a directory.")
    if not args.csv_file.is_file():
        raise SystemExit(f"CSV file '{args.csv_file}' does not exist or is not a file.")

    metadata = load_metadata(args.csv_file)
    output_dir: Path = args.output_dir
    unmatched_dir = output_dir / "unmatched"
    output_dir.mkdir(parents=True, exist_ok=True)

    folders = list(iter_file_folders(args.input_dir))
    if args.test is not None:
        folders = folders[: max(args.test, 0)]

    for folder in folders:
        process_folder(folder, metadata, output_dir, unmatched_dir)


if __name__ == "__main__":
    main()
