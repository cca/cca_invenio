"""Pytest configuration and fixtures for InvenioRDM tests.

These tests are designed to run against a live InvenioRDM instance.
Make sure your development instance is running before executing tests:
    invenio-cli services start
    invenio-cli run
"""

import sys
from pathlib import Path

import pytest

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
def identity():
    """Return system identity for tests."""
    from invenio_access.permissions import system_identity

    return system_identity


@pytest.fixture
def minimal_record():
    """Return minimal valid record metadata."""
    return {
        "files": {"enabled": False},  # metadata-only record
        "metadata": {
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "family_name": "Doe",
                        "given_name": "John",
                    }
                }
            ],
            "title": "Test Record",
            "publication_date": "2024-01-01",
            "publisher": "Test Publisher",
        },
    }


@pytest.fixture
def record_with_archives_series():
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
            "title": "Test Archives Record",
            "publication_date": "1975-01-01",
            "publisher": "CCA/C",
        },
        "custom_fields": {
            "cca:archives_series": {
                "series": "II. College Life",
                "subseries": "3. Events",
            }
        },
    }
