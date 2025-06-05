import click
from invenio_accounts import current_accounts as accounts
from invenio_db import db
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_records_resources.services.uow import UnitOfWork


@click.command()
@click.argument("record-id", type=str)
@click.argument("email", type=str)
def change_owner(record_id, email):
    """Change the owner of a record. Run with `invenio shell`."""
    try:
        record = service.record_cls.pid.resolve(record_id)
    except:
        return click.echo(f"Record with ID {record_id} not found.", err=True)

    # this doesn't throw an error if the user is not found
    user = accounts.datastore.get_user(email)
    if not user:
        return click.echo(f"User with email {email} not found.", err=True)

    record.parent.access.owned_by = user
    # # not needed here. but to get an identity from a user:
    # from invenio_access.permissions import any_user
    # from invenio_access.utils import get_identity
    # identity = get_identity(user)
    # identity.provides.add(any_user)

    # use UnitOfWork to save changes, not record.commit() & db.session.commit()
    # https://inveniordm.docs.cern.ch/develop/topics/uow/
    with UnitOfWork(db.session) as uow:
        uow.register(
            ParentRecordCommitOp(record.parent, indexer_context={"service": service})
        )
        uow.commit()

    click.echo(
        f"{email} now owns {record_id}: https://127.0.0.1:5000/api/records/{record_id}"
    )


if __name__ == "__main__":
    change_owner()
