"""Pytest configuration and fixtures for InvenioRDM tests.

These tests are designed to run against a live InvenioRDM instance.
Make sure your development instance is running before executing tests:
    invenio-cli services start
    invenio-cli run
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from flask_principal import Identity

# Add the site directory to Python path so we can import cca module
site_path = Path(__file__).parent.parent / "site"
if str(site_path) not in sys.path:
    sys.path.insert(0, str(site_path))


@pytest.fixture(scope="session")
def app():
    """Create application instance for testing.

    This uses the actual Flask app from the running instance context.
    Tests will use the same database and search backend as your dev instance.
    """
    try:
        from flask import current_app
        from invenio_app.factory import create_app

        # Check if we're already in an app context
        try:
            app = current_app
            # Verify it's accessible
            _ = app.config
            return app
        except RuntimeError:
            # No app context, create one
            app = create_app()
            ctx = app.app_context()
            ctx.push()
            return app
    except ImportError as e:
        pytest.skip(f"Could not import Flask app: {e}")


@pytest.fixture(scope="session")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def identity() -> Identity:
    """Return system identity for tests."""
    from invenio_access.permissions import system_identity

    return system_identity


@pytest.fixture
def minimal_record() -> dict[str, Any]:
    """Return minimal valid record metadata."""
    return {
        "files": {"enabled": False},  # metadata-only record
        "metadata": {
            "resource_type": {"id": "publication"},
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "family_name": "Kahlo",
                        "given_name": "Frida",
                    }
                }
            ],
            "publication_date": date.today().isoformat(),
            "title": "Test Record",
        },
    }


@pytest.fixture
def record_with_archives_series() -> dict[str, Any]:
    """Return record with archives series custom field."""
    return {
        "files": {"enabled": False},  # metadata-only record
        "metadata": {
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "family_name": "Sommer",
                        "given_name": "Robert",
                    }
                }
            ],
            "publication_date": date.today().isoformat(),
            "publisher": "California College of the Arts",
            "title": "Test Archives Record",
        },
        "custom_fields": {
            "cca:archives_series": {
                "series": "III. College Life",
                "subseries": "3. Events",
            }
        },
    }


@pytest.fixture
def tombstone() -> dict[str, bool | str]:
    """Return standard tombstone data for test record cleanup.

    Args:
        note: Optional note explaining the deletion reason

    Returns:
        dict: Tombstone data structure for delete_record calls
    """
    return {
        "note": "Test Cleanup",
        "is_visible": False,
    }
