# TB-Rename-Files

A small command-line helper that renames Toniebox `.taf` files based on a CSV
mapping or simply by their folder ids.

## Requirements

* Python 3.9 or newer

## Installation

Install the package in editable mode so that the `td-rename` command becomes
available:

```bash
git clone <repository-url>
cd TB-Rename-Files
pip install -e .
```

You can still invoke the legacy script directly with `python rename_files.py`,
but the recommended workflow is to use the installed CLI entry point.

## Preparing the input data

1. **Input directory** – contains one subdirectory per file. Each subdirectory
   should hold exactly one `.taf` file whose parent folder name represents the
   file ID (for example, `12345678`).
2. **CSV metadata file** – must provide the columns `Name`, `Series`, and
   `Episode`. The value from the `Name` column is matched (case-insensitively)
   against the folder name. The `Series` and `Episode` values are optional but
   at least one of them should be present to create a descriptive filename.

## Usage

### Rename using metadata

```bash
td-rename from-csv <input_dir> <mapping.csv> <output_dir>
```

For example:

```bash
td-rename from-csv ~/toniebox/input tonies.csv ~/toniebox/output
```

This command copies each file from `~/toniebox/input/<id>/` into the flat
output directory `~/toniebox/output`. When metadata is available, files are
renamed to `<Series> - <Episode>.taf`. Files without metadata are moved to the
`unmatched/` subdirectory and keep their original ID as the filename.

### Rename using folder ids

```bash
td-rename with-id <input_dir> <output_dir>
```

This mode simply copies each file from `<input_dir>/<id>/` to `<output_dir>` and
renames it to `<id>.taf`. Use it when you only need to normalise file names
without relying on a CSV mapping.

### Dry-run / limiting the run

Use the `--test` flag to process only the first *N* folders. This is useful to
validate the workflow on a small subset, for example:

```bash
td-rename with-id ~/toniebox/input ~/toniebox/output --test 2
```

The flag is also available for the `from-csv` command.

## Tips

* Existing files in the output directory are preserved. When a filename already
  exists, the script appends `_1`, `_2`, … to create a unique name.
* Filenames are sanitised so that path separators or control characters are
  replaced with underscores.
* The script copies files (it does not move them), so the source directories
  remain untouched.
