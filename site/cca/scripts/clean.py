import os
from pathlib import Path

import click

data_filenames: list[str] = ["courses.json", "employee_data.json", "student_data.json"]
user_data_paths: list[Path] = [
    Path("app_data") / "users.yaml",
    Path("app_data") / "vocabularies" / "names.yaml",
]


def print_verbose(verbose, *args) -> None:
    """Print if verbose is True"""
    if verbose:
        print(*args)


@click.command()
@click.help_option("-h", "--help")
@click.option("-u", "--users", is_flag=True, help="Delete names.yaml and users.yaml.")
@click.option("-v", "--verbose", is_flag=True, help="Print info about deleted files.")
def clean(users: bool, verbose: bool) -> None:
    """Delete data files including ones with personal information. Does not delete id-map.json files."""
    if users:
        for p in user_data_paths:
            try:
                os.remove(p)
                print_verbose(verbose, f"Deleted {p}")
            except FileNotFoundError:
                print_verbose(verbose, f"File not found: {p}")
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if filename in data_filenames:
                p: Path = Path(dirpath) / filename
                os.remove(p)
                print_verbose(verbose, f"Deleted {p}")
