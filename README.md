# TB-Rename-Files

A small command-line helper that renames Toniebox `.taf` files based on a CSV mapping.

## Requirements

* Python 3.8 or newer

## Installation

Clone the repository and make the script executable:

```bash
git clone <repository-url>
cd TB-Rename-Files
chmod +x rename_files.py
```

Alternatively, call the script through the Python interpreter without changing permissions:

```bash
python3 rename_files.py --help
```

## Preparing the input data

1. **Input directory** – contains one subdirectory per file. Each subdirectory
   should hold exactly one `.taf` file whose parent folder name represents the
   file ID (for example, `12345678`).
2. **CSV metadata file** – must provide the columns `Name`, `Series`, and
   `Episode`. The value from the `Name` column is matched (case-insensitively)
   against the folder name. The `Series` and `Episode` values are optional but
   at least one of them should be present to create a descriptive filename.

## Usage

```
./rename_files.py <input_dir> <mapping.csv> <output_dir>
```

For example:

```bash
./rename_files.py ~/toniebox/input tonies.csv ~/toniebox/output
```

This command copies each file from `~/toniebox/input/<id>/` into the flat
output directory `~/toniebox/output`. When metadata is available, files are
renamed to `<Series> - <Episode>.taf`. Files without metadata are moved to the
`unmatched/` subdirectory and keep their original ID as the filename.

### Dry-run / limiting the run

Use the `--test` flag to process only the first *N* folders. This is useful to
validate the workflow on a small subset:

```bash
./rename_files.py ~/toniebox/input tonies.csv ~/toniebox/output --test 5
```

## Tips

* Existing files in the output directory are preserved. When a filename already
  exists, the script appends `_1`, `_2`, … to create a unique name.
* Filenames are sanitised so that path separators or control characters are
  replaced with underscores.
* The script copies files (it does not move them), so the source directories
  remain untouched.
