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
            "full_name": "Finn 2187",
        },
    },
    {
        "email": "library-test-student-2@cca.edu",
        "user_profile": {
            "full_name": "Rey Skywalker",
            "affiliations": "California College of the Arts",
        },
        "username": "library-test-student-2",
        "active": True,
        "confirmed_at": datetime.now(),
    },
    {
        "email": "library-test-faculty-1@cca.edu",
        "user_profile": {
            "full_name": "Leia Organa",
            "affiliations": "California College of the Arts",
        },
        "username": "library-test-faculty-1",
        "active": True,
        "confirmed_at": datetime.now(),
    },
    {
        "email": "library-test-faculty-2@cca.edu",
        "user_profile": {
            "full_name": "Kylo Ren",
            "affiliations": "California College of the Arts",
        },
        "username": "library-test-faculty-2",
        "active": True,
        "confirmed_at": datetime.now(),
    },
    {
        "email": "library-test-manager-1@cca.edu",
        "user_profile": {
            "full_name": "Admiral Ackbar",
            "affiliations": "California College of the Arts",
        },
        "username": "library-test-manager-1",
        "active": True,
        "confirmed_at": datetime.now(),
    },
]


@with_appcontext
def add_users() -> None:
    for user in users:
        # this method returns the user if we need to do something with it
        accounts.datastore.create_user(**user)
    accounts.datastore.commit()
    # ! how do we update the index too? `invenio rdm rebuild-all-indices -o users`
