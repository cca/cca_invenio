"""Tests for CLI utilities in site/cca/scripts/."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
def test_add_users_command(app):
    """Test the add_users CLI command."""
    from cca.scripts.add_users import add_users
    from click.testing import CliRunner
    from invenio_accounts import current_accounts as accounts

    runner = CliRunner()

    # Create temporary user JSON file
    test_users = [
        {
            "email": "test-cli-user@example.com",
            "username": "testcliuser",
            "password": "TestPassword123!",
            "active": True,
            "user_profile": {
                "full_name": "Test CLI User",
                "affiliations": "Test University",
            },
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_users, f)
        temp_file = Path(f.name)

    try:
        # Run the command
        result = runner.invoke(add_users, ["-f", str(temp_file)])

        # Check the command succeeded or user already exists
        assert result.exit_code == 0 or "already exists" in result.output

        # Verify user was created (or already existed)
        with app.app_context():
            user = accounts.datastore.get_user("test-cli-user@example.com")
            assert user is not None
            assert user.email == "test-cli-user@example.com"
    finally:
        # Clean up temp file
        temp_file.unlink(missing_ok=True)
    # TODO delete all users with the test email address


@pytest.mark.integration
def test_add_users_invalid_json(app):
    """Test add_users command with invalid JSON."""
    from cca.scripts.add_users import add_users
    from click.testing import CliRunner

    runner = CliRunner()

    # Create temp file with invalid JSON (not a list)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"not": "a list"}, f)
        temp_file = Path(f.name)

    try:
        result = runner.invoke(add_users, ["-f", str(temp_file)])
        assert result.exit_code != 0
        assert "not a list" in result.output
    finally:
        temp_file.unlink(missing_ok=True)


@pytest.mark.unit
def test_add_communities_validation():
    """Test that add_communities validates community data."""
    # This test doesn't need to actually create communities
    # but tests the validation using the Community model
    from cca.models import Community

    valid_community = {
        "slug": "test-community",
        "access": {
            "visibility": "public",
            "member_policy": "closed",
            "record_policy": "open",
        },
        "metadata": {
            "title": "Test Community",
            "type": {"id": "topic"},
        },
    }

    # Should not raise validation error
    community = Community(**valid_community)
    assert community.slug == "test-community"
    assert community.metadata.title == "Test Community"


@pytest.mark.unit
def test_add_communities_invalid_slug():
    """Test that invalid community slugs are caught."""
    from cca.models import Community

    invalid_community = {
        "slug": "Invalid Slug!",  # Spaces and special chars not allowed
        "access": {
            "visibility": "public",
            "member_policy": "closed",
            "record_policy": "open",
        },
        "metadata": {
            "title": "Test Community",
            "type": {"id": "topic"},
        },
    }

    with pytest.raises(Exception):  # Pydantic ValidationError
        Community(**invalid_community)


@pytest.mark.unit
def test_groups_sync_functions():
    """Test utility functions from groups_sync script."""
    import importlib.util
    import sys
    from pathlib import Path

    # Import groups_sync module
    module_path = (
        Path(__file__).parent.parent / "site" / "cca" / "scripts" / "groups_sync.py"
    )
    spec = importlib.util.spec_from_file_location("groups_sync", str(module_path))
    if spec and spec.loader:
        gs = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = gs
        spec.loader.exec_module(gs)

        # Test slugify function
        assert gs.slugify("Fine Art") == "fine_art"
        assert gs.slugify("CS&IT") == "cs_it"
        assert gs.slugify("") == "unnamed"
        assert gs.slugify("  Multiple   Spaces  ") == "multiple_spaces"
        assert gs.slugify("Special-Chars!@#$%") == "special_chars"


@pytest.mark.unit
def test_user_model_validation():
    """Test User model validation."""
    from cca.models import User

    valid_user = {
        "email": "valid@example.com",
        "username": "validuser",
        "password": "ValidPassword123!",
        "active": True,
        "user_profile": {
            "full_name": "Valid User",
        },
    }

    user = User(**valid_user)
    assert user.email == "valid@example.com"
    assert user.active is True


@pytest.mark.unit
def test_user_model_invalid_email():
    """Test that User model catches invalid emails."""
    from cca.models import User

    invalid_user = {
        "email": "not-an-email",
        "password": "Password123!",
        "active": True,
    }

    with pytest.raises(Exception):  # Pydantic ValidationError
        User(**invalid_user)
