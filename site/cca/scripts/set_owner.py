from os import environ
from typing import Any

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts as accounts
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as records


def set_record_owner(record, owner) -> None:
    parent = record.parent
    parent.access.owner = owner
    parent.commit()


def set_single_owner(record_id: str, email: str) -> bool:
    """Set the owner of a single record.

    Args:
        record_id: The Invenio record ID
        email: Email address of the owner

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
        record = records.read(system_identity, id_=record_id)._record
    except Exception as e:
        click.echo(f"ERROR: could not find record {record_id}: {e}", err=True)
        return False

    try:
        set_record_owner(record, user)
        db.session.commit()
        if records.indexer:
            records.indexer.index(record)
        return True
    except Exception as e:
        click.echo(f"ERROR: failed to set owner: {e}", err=True)
        return False


@click.command()
@click.help_option("-h", "--help")
@click.argument("record_id", type=click.STRING, required=False)
@click.argument("email", type=click.STRING, required=False)
@click.option(
    "--map-file",
    type=click.Path(exists=True, readable=True, writable=True),
    help="Path to id-map.json file; processes all pending owners if no record_id given",
)
@click.option(
    "--host",
    default=lambda: environ.get("HOST") or environ.get("INVENIO_HOST", ""),
    help="Invenio hostname for display purposes",
    type=str,
)
@with_appcontext
def set_owner(
    record_id: str | None, email: str | None, map_file: str | None, host: str
) -> None:
    """Set the owner of record(s).

    Two modes of operation:

    1. Single record mode (record_id required):
       Sets owner to the provided email or, if no email given, to the email
       of the first creator in the metadata.

    2. Batch mode (--map-file required, no record_id):
       Processes all records in the id-map that have an owner listed but
       no corresponding set_owner event.

    Examples:
        # Set owner from creator metadata
        invenio cca set-owner abc12-xyz34

        # Set owner to specific email
        invenio cca set-owner abc12-xyz34 user@example.com

        # Batch process owners from migration map
        invenio cca set-owner --map-file migration/id-map.json
    """
    # Batch mode: process map file
    if map_file and not record_id:
        from cca.scripts.id_map_utils import get_pending_owners, is_uuid

        pending: list[dict[str, Any]] = get_pending_owners(map_file)

        if not pending:
            click.echo("No pending owners found in id-map")
            return

        click.echo(f"Found {len(pending)} records with pending owners")

        fail_count = 0
        success_count = 0

        for item in pending:
            rec_id = item["record_id"]
            owner = item["owner"]
            title = item["title"]

            url: str = f"https://{host}/records/{rec_id}" if host else rec_id
            click.echo(f'Processing: {url} "{title}"')
            click.echo(f"Owner: {owner}")

            if is_uuid(owner):
                click.echo(f"WARNING: skipping UUID owner {owner}", err=True)
                fail_count += 1
                continue

            # Try to find user by email & if no "@", username
            user = accounts.datastore.find_user(email=owner)
            if not user and "@" not in owner:
                user = accounts.datastore.find_user(username=owner)

            if not user:
                click.echo(f"WARNING: user not found {owner}", err=True)
                fail_count += 1
                continue

            # Set the owner
            if set_single_owner(rec_id, user.email):
                click.echo(f"✓ Set {url} owner to {user.email}")
                # Record the event
                try:
                    from cca.scripts.id_map_utils import record_event

                    record_event(map_file, rec_id, "set_owner", {"email": user.email})
                    success_count += 1
                except Exception as e:
                    click.echo(f"WARNING: failed to record event: {e}", err=True)
            else:
                fail_count += 1

        click.echo(
            f"Completed: {success_count} owners set, {fail_count} failed/skipped."
        )
        return

    # Single record mode
    if not record_id:
        click.echo(
            "ERROR: Either provide record_id, or use --map-file for batch mode",
            err=True,
        )
        exit(1)

    record = records.read(system_identity, id_=record_id)._record

    if not email:
        click.echo("No owner specified, looking at Creators metadata")
        # get owner email from creator metadata, one creator is required
        creator_ids: list[dict[str, str]] = record.metadata["creators"][0][
            "person_or_org"
        ]["identifiers"]
        creator_emails: list[dict[str, str]] = list(
            filter(lambda i: i["scheme"] == "email", creator_ids)
        )
        if len(creator_emails) < 1:
            click.echo("ERROR: no email found for first creator. Creator:", err=True)
            click.echo(record.metadata["creators"][0], err=True)
            exit(1)
        email = creator_emails[0]["identifier"]

    # Set single owner
    if set_single_owner(record_id, email):
        url: str = f"https://{host}/records/{record_id}" if host else record_id
        click.echo(f"✓ Set {url} owner to {email}")
    else:
        exit(1)


if __name__ == "__main__":
    set_owner()
