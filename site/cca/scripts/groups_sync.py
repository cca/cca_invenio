import json
import os
import re
import subprocess
from sys import stderr
from typing import Any, Dict, List

import click
from google.cloud import storage

# TODO should `invenio` calls be programmatic instead? It speeds things up greatly.
# https://inveniordm.docs.cern.ch/operate/customize/authentication/#add-groups
# from invenio_accounts.proxies import current_datastore
# current_datastore.create_role(name="ID", description="Group Name")
# current_datastore.commit() # would still need a reindex afterwards


def download_blob(bucket_name: str, filename: str, destination_filename: str) -> None:
    """Download a blob from GCS to a local file."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.download_to_filename(destination_filename)
    print(f"Downloaded {filename} to {destination_filename}.")


def slugify(name: str) -> str:
    """Make a safe group id from a program name.

    Lowercase, replace non-alnum with underscore, collapse multiple underscores.
    """
    name = name.lower() or "unnamed"
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def run_cmd(cmd: List[str], dry_run: bool) -> None:
    """Run a command or print it if dry_run is True."""
    cmd_string = " ".join(cmd)

    print(cmd_string)
    if dry_run:
        return

    try:
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(
            f"ERROR {e.returncode} command failed: {cmd_string}\n  exit: ", file=stderr
        )


def process_students(
    students: List[Dict[str, Any]], create_groups: bool, dry_run: bool
) -> None:
    """Create/populate groups for student data.

    students is expected to be a list of objects with at least:
      - inst_email: student email
      - programs: array of program names (can be empty)
    """
    groups: Dict[str, str] = {}  # program_name -> group_id

    for s in students:
        email: str | None = s.get("inst_email")
        if not email:
            print(
                f"Skipping student {s.get('first_name')} {s.get('last_name')} ({s.get('username')}) without email"
            )
            continue

        programs: list[dict[str, str]] = s.get("programs") or []

        # filter to majors
        for prog in filter(lambda p: p.get("program_type") == "Major", programs):
            group_id: str = f"{slugify(prog['program'])}_majors"
            group_name: str = f"{prog['program']} Majors"

            if group_id not in groups:
                groups[group_name] = group_id
                if create_groups:
                    run_cmd(
                        ["invenio", "roles", "create", group_id, "-d", group_name],
                        dry_run,
                    )

            # add the user to the group
            run_cmd(["invenio", "roles", "add", email, group_id], dry_run)


# ! this will not add program admins to faculty group e.g. pacenti
def process_employees(
    employees: List[Dict[str, Any]], create_groups: bool, dry_run: bool
) -> None:
    """Create/populate groups for employee (faculty) data. We don't do anything
    with staff accounts yet.

    employees is expected to be a list of objects with at least:
      - work_email: employee email
      - program: program name (string, can be null)
    """
    groups: Dict[str, str] = {}  # program_name -> group_id

    for e in employees:
        email: str | None = e.get("work_email")
        if not email:
            print(
                f"Skipping employee {e.get('first_name')} {e.get('last_name')} ({e.get('username')}) without email"
            )
            continue

        prog: str | None = e.get("program")
        if not prog:
            print(f"Skipping employee {email} without program")
            continue

        group_id: str = f"{slugify(prog)}_faculty"
        group_name: str = f"{prog} Faculty"

        if prog not in groups:
            groups[prog] = group_id
            if create_groups:
                run_cmd(
                    ["invenio", "roles", "create", group_id, "-d", group_name], dry_run
                )

        run_cmd(["invenio", "roles", "add", email, group_id], dry_run)


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "--bucket",
    default=lambda: os.getenv("USERS_BUCKET_NAME", "integration-success"),
    help="GCS bucket name to download from",
    type=click.STRING,
)
@click.option(
    "--employee-blob",
    default=lambda: os.getenv("EMPLOYEE_BLOB_NAME", "employee_data.json"),
    help="Filename of remote employee data (employee_data.json)",
    type=click.STRING,
)
@click.option(
    "--student-blob",
    default=lambda: os.getenv("STUDENT_BLOB_NAME", "student_data.json"),
    help="Filename of remote student data (student_data.json)",
    type=click.STRING,
)
@click.option(
    "--employee-dest",
    default=lambda: os.getenv("EMPLOYEE_DEST_FILE", "employee_data.json"),
    help="Local filename for employee data (employee_data.json)",
    type=click.Path(),
)
@click.option(
    "--student-dest",
    default=lambda: os.getenv("STUDENT_DEST_FILE", "student_data.json"),
    help="Local filename for student data (student_data.json)",
    type=click.Path(),
)
@click.option("--employees", is_flag=True, help="Process employees/faculty data")
@click.option("--students", is_flag=True, help="Process students data")
@click.option(
    "--create-groups",
    is_flag=True,
    help="Create groups in Invenio before populating them",
)
@click.option(
    "--reindex",
    is_flag=True,
    help="Reindex groups after updating (runs invenio rdm rebuild-all-indices -o groups)",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Print the Invenio commands instead of executing them",
)
def main(
    bucket: str,
    employee_blob: str,
    student_blob: str,
    employee_dest: str,
    student_dest: str,
    employees: bool,
    students: bool,
    create_groups: bool,
    reindex: bool,
    dry_run: bool,
):
    """Download employee and/or student JSON from GCS and add users to Invenio groups.

    Students are added to "<Program Name> Majors" groups (based on the "programs" array).
    Faculty/employees are added to "<Program Name> Faculty" groups (based on the "program" property).

    Use --create-groups to run `invenio roles create GROUP_ID -d "Group Name"` before adding members.
    Use -n or --dry-run to only print the commands that would be run.
    """
    if not (employees or students):
        click.echo(
            "Error: pass either --employees and/or --students flag(s).", err=True
        )
        return exit(1)

    if employees:
        emp_data = None
        if dry_run:
            if os.path.exists(employee_dest):
                click.echo(f"Dry run: no download, using local {employee_dest}")
                with open(employee_dest, "r") as f:
                    emp_data = json.load(f).get("Report_Entry")
            else:
                click.echo(
                    f"Dry run: no local {employee_dest} found; skipping employees processing"
                )
        else:
            click.echo(
                f"Downloading employees from gs://{bucket}/{employee_blob} -> {employee_dest}"
            )
            download_blob(bucket, employee_blob, employee_dest)
            with open(employee_dest, "r") as f:
                emp_data = json.load(f).get("Report_Entry")

        if not emp_data:
            click.echo("No employee data to process", err=True)
        elif not isinstance(emp_data, list):
            click.echo(
                "Employee data is not a list; aborting employees processing", err=True
            )
        else:
            process_employees(emp_data, create_groups, dry_run)

    if students:
        stu_data = None
        if dry_run:
            if os.path.exists(student_dest):
                click.echo(f"Dry run: no download, using local {student_dest}")
                with open(student_dest, "r") as f:
                    stu_data = json.load(f).get("Report_Entry")
            else:
                click.echo(
                    f"Dry run: no local {student_dest} found; skipping students processing"
                )
        else:
            click.echo(
                f"Downloading students from gs://{bucket}/{student_blob} -> {student_dest}"
            )
            download_blob(bucket, student_blob, student_dest)
            with open(student_dest, "r") as f:
                stu_data = json.load(f).get("Report_Entry")

        if not stu_data:
            click.echo("No student data to process", err=True)
        elif not isinstance(stu_data, list):
            click.echo(
                "Student data is not a list; aborting students processing", err=True
            )
        else:
            process_students(stu_data, create_groups, dry_run)

    if reindex:
        run_cmd(["invenio", "rdm", "rebuild-all-indices", "-o", "groups"], dry_run)


if __name__ == "__main__":
    main()
