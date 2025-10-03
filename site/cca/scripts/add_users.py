import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import click
from flask.cli import with_appcontext
from invenio_accounts import current_accounts as accounts
from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    # we require full_name
    affiliations: Optional[str] = None
    full_name: str


class User(BaseModel):
    # we require email & username
    active: Optional[bool] = None
    confirmed_at: Optional[datetime] = None
    email: EmailStr
    username: str  # TODO match username regex
    user_profile: UserProfile


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--file",
    help="JSON file of users.",
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--reindex",
    is_flag=True,
    help="Reindex afterwards (runs invenio rdm rebuild-all-indices -o users)",
)
@with_appcontext
def add_users(file: Path, reindex: bool) -> None:
    """Add user accounts to Invenio. Automatically activates & confirms the accounts.
    To update the names vocabulary, see `invenio vocabularies update -v names`."""
    # TODO add roles?
    with open(file, "r") as fh:
        users: list[dict[str, Any]] = json.load(fh)
        if not isinstance(users, list):
            click.echo("ERROR: users JSON is not a list, exiting", err=True)
            exit(1)

        for user in users:
            user["confirmed_at"] = datetime.now()
            User(**user)  # validate user data before creating
            # this method returns the user if we need to do something with it
            accounts.datastore.create_user(**user)
        accounts.datastore.commit()

    if reindex:
        subprocess.call(
            ["invenio", "rdm", "rebuild-all-indices", "-o", "users"],
            stderr=subprocess.DEVNULL,
        )
