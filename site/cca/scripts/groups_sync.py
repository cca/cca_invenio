import json
import os
import re
import subprocess
from typing import Any, Dict, List

import click
from flask import current_app
from flask.cli import with_appcontext
from google.cloud import storage
from werkzeug.local import LocalProxy


class MockDatastore:
    def add_role_to_user(self, email: str, role: str) -> None:
        pass

    def commit(self):
        pass

    def create_role(self, name: str, description: str) -> None:
        pass

    def get_user(self, email: str):
        pass


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


def create_role(role_id: str, description: str, datastore=None) -> None:
    """Create a role using Invenio internal API when available, otherwise print."""
    if datastore is None:
        datastore = MockDatastore()
    try:
        datastore.create_role(name=role_id, description=description)
        print(f"Created role {role_id}")
    except Exception as e:
        print(f"Failed to create role {role_id}: {e}")


def add_user_to_role(
    email: str,
    role: str,
    datastore=None,
) -> None:
    """Add a user to a role using Invenio internal API when available, otherwise print."""
    if datastore is None:
        datastore = MockDatastore()
        user = email
    else:
        user = datastore.get_user(email)
    if user:
        try:
            datastore.add_role_to_user(email, role)
            print(f"Added {email} to {role}")
        except Exception as e:
            print(f"Failed to add {email} to {role}: {e}")
    else:
        print(f"User does not exist: {email}")


def process_students(
    students: List[Dict[str, Any]], create_groups: bool, datastore=None
) -> None:
    """Create/populate groups for student data.

    students is expected to be a list of objects with at least:
      - inst_email: student email
      - programs: array of program names (can be empty)
    """
    groups: set[str] = set()  # program_name -> group_id

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
                groups.add(group_id)
                if create_groups:
                    create_role(group_id, group_name, datastore)

            # add the user to the group
            add_user_to_role(email, group_id, datastore)


# ! this will not add program admins to faculty group e.g. pacenti
def process_employees(
    employees: List[Dict[str, Any]], create_groups: bool, datastore=None
) -> None:
    """Create/populate groups for employee (faculty) data. We don't do anything
    with staff accounts yet.

    employees is expected to be a list of objects with at least:
      - work_email: employee email
      - program: program name (string, can be null)
    """
    groups: set[str] = set()

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

        if group_id not in groups:
            groups.add(group_id)
            if create_groups:
                create_role(group_id, group_name, datastore)

        add_user_to_role(email, group_id, datastore)


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
@with_appcontext
def groups_sync(
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

    datastore = LocalProxy(lambda: current_app.extensions["security"].datastore)

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
            process_employees(emp_data, create_groups, datastore)

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
            process_students(stu_data, create_groups, datastore)

    datastore.commit()

    if reindex:
        subprocess.call(
            ["invenio", "rdm", "rebuild-all-indices", "-o", "groups"],
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    groups_sync()
