"""Command line interface for td_rename."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from .csv_mode import rename_from_csv
from .id_mode import rename_with_id


def _positive_limit(value: str) -> int:
    return int(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rename Toniebox files using a CSV mapping or folder ids.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    csv_parser = subparsers.add_parser(
        "from-csv",
        help="Rename files using the Name/Series/Episode CSV mapping.",
    )
    csv_parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing folders whose names represent file ids.",
    )
    csv_parser.add_argument(
        "csv_file",
        type=Path,
        help="CSV file with the columns 'Name', 'Series', 'Episode'.",
    )
    csv_parser.add_argument(
        "output_dir",
        type=Path,
        help="Destination directory that will receive the renamed files.",
    )
    csv_parser.add_argument(
        "--test",
        type=_positive_limit,
        metavar="N",
        default=None,
        help=(
            "Only process the first N folders. Useful for quickly testing the workflow",
        ),
    )
    csv_parser.set_defaults(func=_run_from_csv)

    id_parser = subparsers.add_parser(
        "with-id",
        help="Rename files to match their folder id.",
    )
    id_parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing folders whose names represent file ids.",
    )
    id_parser.add_argument(
        "output_dir",
        type=Path,
        help="Destination directory that will receive the renamed files.",
    )
    id_parser.add_argument(
        "--test",
        type=_positive_limit,
        metavar="N",
        default=None,
        help="Only process the first N folders to test the behaviour.",
    )
    id_parser.set_defaults(func=_run_with_id)

    return parser


def _run_from_csv(args: argparse.Namespace) -> None:
    rename_from_csv(args.input_dir, args.csv_file, args.output_dir, limit=args.test)


def _run_with_id(args: argparse.Namespace) -> None:
    rename_with_id(args.input_dir, args.output_dir, limit=args.test)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    func: Callable[[argparse.Namespace], None] = args.func
    func(args)


if __name__ == "__main__":
    main()
