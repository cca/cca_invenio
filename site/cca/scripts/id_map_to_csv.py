#!/usr/bin/env python3
import sys
from pathlib import Path

import click
from cca.scripts.id_map_utils import id_map_to_csv


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(path_type=Path),
    default="id-map.csv",
    help="Output CSV file path (default: id-map.csv)",
)
def main(input_file: Path, output_file: Path) -> None:
    """Convert an ID map JSON file to CSV format.

    INPUT_FILE: Path to the id-map.json file to convert
    """
    try:
        id_map_to_csv(input_file, output_file)
        click.echo(f"✓ Converted {input_file} to {output_file}")
    except FileNotFoundError:
        click.echo(f"✗ Error: File {input_file} not found", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
