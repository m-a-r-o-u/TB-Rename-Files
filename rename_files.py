#!/usr/bin/env python3
"""Backward compatible CLI that renames Toniebox files via CSV metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

from td_rename.csv_mode import rename_from_csv


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


def main() -> None:
    args = parse_arguments()
    try:
        rename_from_csv(args.input_dir, args.csv_file, args.output_dir, limit=args.test)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
