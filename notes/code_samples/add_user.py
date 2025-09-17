from datetime import datetime
from typing import Any

from flask.cli import with_appcontext
from invenio_accounts import current_accounts as accounts

# TODO roles?
users: list[dict[str, Any]] = [
    {
        "active": True,
        "confirmed_at": datetime.now(),
        "email": "library-test-student-1@cca.edu",
        "username": "library-test-student-1",
        "user_profile": {
            "affiliations": "California College of the Arts",
            "full_name": "Kylo Ren",
        },
    }
]


@with_appcontext
def add_users() -> None:
    for user in users:
        # this method returns the user if we need to do something with it
        accounts.datastore.create_user(**user)
    accounts.datastore.commit()
    # ! how do we update the index too? `invenio rdm rebuild-all-indices -o users`
