"""Add a user as an editor (manager) to a record."""

from os import environ
from typing import Any

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts as accounts
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as records


def add_single_editor(record_id: str, email: str, permission: str = "manage") -> bool:
    """Add a single user as an editor to a record.

    Args:
        record_id: The Invenio record ID
        email: Email address of the user
        permission: Permission level (view, preview, edit, manage)

    Returns:
        True if successful, False otherwise
    """
    # Get the user
    user = accounts.datastore.get_user(email)
    if not user:
        click.echo(f"ERROR: no user found with email {email}", err=True)
        return False

    # Get the record
    try:
        record_item = records.read(system_identity, id_=record_id)
        assert record_item is not None
    except Exception as e:
        click.echo(f"ERROR: could not find record {record_id}: {e}", err=True)
        return False

    # Create the grant
    grant_data: dict[str, Any] = {
        "grants": [
            {
                "subject": {"type": "user", "id": str(user.id)},
                "permission": permission,
                "origin": "cli:add-editor",
            }
        ]
    }

    try:
        records.access.bulk_create_grants(
            system_identity, record_id, data=grant_data, expand=False
        )
        db.session.commit()
        return True
    except Exception as e:
        click.echo(f"ERROR: failed to add editor: {e}", err=True)
        return False


@click.command()
@click.help_option("-h", "--help")
@click.argument("record_id", type=click.STRING, required=False)
@click.argument("email", type=click.STRING, required=False)
@click.option(
    "--permission",
    type=click.Choice(["view", "preview", "edit", "manage"]),
    default="manage",
    help="Permission level to grant (default: manage)",
)
@click.option(
    "--map-file",
    type=click.Path(exists=True, readable=True, writable=True),
    help="Path to id-map.json file; processes all pending collaborators if no record_id given",
)
@click.option(
    "--host",
    default=lambda: environ.get("HOST") or environ.get("INVENIO_HOST", ""),
    help="Invenio hostname for display purposes",
    type=str,
)
@with_appcontext
def add_editor(
    record_id: str | None,
    email: str | None,
    permission: str,
    map_file: str | None,
    host: str,
) -> None:
    """Add user(s) as editor(s) to record(s). This has two modes of operation:

    1. Single record mode (record_id and email required): Adds one user to one record, optionally recording in id-map.

    2. Batch mode (--map-file required, no id/email): Processes all records in the id-map that have collaborators listed but no corresponding add_collaborator event. Looks up user emails by username.

    Add single editor:
    invenio cca add-editor abc12-xyz34 user@example.com

    Add with custom permission:
    invenio cca add-editor abc12-xyz34 user@example.com --permission edit

    Batch process collaborators from migration map:
    invenio cca add-editor --map-file migration/id-map.json
    """
    # Batch mode: process map file
    if map_file and not record_id and not email:
        from cca.scripts.id_map_utils import (
            get_pending_collaborators,
            is_uuid,
            record_event,
        )

        pending: list[dict[str, Any]] = get_pending_collaborators(map_file)

        if not pending:
            click.echo("No pending collaborators found in id-map")
            return

        click.echo(f"Found {len(pending)} records with pending collaborators")

        fail_count = 0
        success_count = 0

        for item in pending:
            rec_id: str = item["record_id"]
            url: str = f"https://{host}/records/{rec_id}" if host else rec_id
            collabs: list[str] = item["collaborators"]
            title: str = item["title"]

            click.echo(f'Processing: {url} "{title}"')
            click.echo(f"Collaborators: {', '.join(collabs)}")

            for collab in collabs:
                if is_uuid(collab):
                    click.echo(
                        f"WARNING: skipping UUID collaborator {collab}",
                        err=True,
                    )
                    fail_count += 1
                    continue

                # Try to find user by username & {username}@cca.edu email
                user = accounts.datastore.find_user(email=collab)
                if not user and "@" not in collab:
                    user = accounts.datastore.find_user(email=f"{collab}@cca.edu")

                if not user:
                    click.echo(f"WARNING: user not found {collab}", err=True)
                    fail_count += 1
                    continue

                # Add the editor
                if add_single_editor(rec_id, user.email, permission):
                    click.echo(
                        f"✓ Added {user.email} to {url} with {permission} permission"
                    )
                    try:
                        record_event(
                            map_file,
                            rec_id,
                            "add_collaborator",
                            {"email": user.email, "permission": permission},
                        )
                        success_count += 1
                    except Exception as e:
                        click.echo(f"WARNING: failed to record event: {e}", err=True)
                else:
                    fail_count += 1

        click.echo(
            f"Completed: {success_count} collaborators added, {fail_count} failed/skipped."
        )
        return

    # Single record mode
    if not record_id or not email:
        click.echo(
            "ERROR: Either provide both record_id and email, or use --map-file for batch mode",
            err=True,
        )
        exit(1)

    url: str = f"https://{host}/records/{record_id}" if host else record_id
    if add_single_editor(record_id, email, permission):
        click.echo(f"✓ Added {email} to {url} with {permission} permission")
    else:
        exit(1)


if __name__ == "__main__":
    add_editor()
