from os import environ as env

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts as accounts
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as records

# ! Rather than changing the owner of a record would it be better/easier to
# ! share to the user with access level manager?


def set_record_owner(record, owner) -> None:
    parent = record.parent
    parent.access.owner = owner
    parent.commit()


@click.command()
@click.help_option("-h", "--help")
@click.argument("record_id", type=click.STRING, required=True)
@click.argument("email", type=click.STRING, required=False)
@with_appcontext
def set_owner(record_id: str, email: str) -> None:
    """Set the owner of a record. Expects a record ID (e.g. b3nb9-3cz11). If no email is provided, the email of the first creator in the metadata is used."""
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

    user = accounts.datastore.get_user(email)
    if not user:
        click.echo(f"ERROR: no user found with email {email}", err=True)
        exit(1)

    set_record_owner(record, user)
    db.session.commit()
    if records.indexer:
        records.indexer.index(record)
    click.echo(
        f"Set owner of record {f'https://{env["INVENIO_HOST"]}/records/' if env['INVENIO_HOST'] else ''}{record_id} to {email}"
    )


if __name__ == "__main__":
    set_owner()
