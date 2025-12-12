"""Tests for CLI utilities in site/cca/scripts/."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def records_service(app):
    """Get records service."""
    from invenio_records_resources.proxies import current_service_registry

    return current_service_registry.get("records")


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


@pytest.mark.integration
def test_add_editor_command(app, minimal_record, identity, records_service, tombstone):
    """Test the add_editor CLI command."""
    from cca.scripts.add_editor import add_editor
    from click.testing import CliRunner
    from invenio_accounts import current_accounts as accounts

    runner = CliRunner()

    # Create a test user
    test_email = "editor-test@example.com"
    test_user_data = {
        "email": test_email,
        "username": "editortest",
        "password": "EditorPass123!",
        "active": True,
    }

    with app.app_context():
        # Create user if doesn't exist
        user = accounts.datastore.get_user(test_email)
        if not user:
            accounts.datastore.create_user(**test_user_data)
            accounts.datastore.commit()

        # Create a test record
        draft = records_service.create(identity, minimal_record)
        record = records_service.publish(identity, draft.id)
        record_id = record.id

        # Run the add_editor command
        result = runner.invoke(add_editor, [record_id, test_email])

        # Check command succeeded
        assert result.exit_code == 0
        assert "Added" in result.output
        assert test_email in result.output
        assert "manage" in result.output

        # Verify the grant was created by checking record access
        record_item = records_service.read(identity, id_=record_id)
        parent = record_item._record.parent
        grants = parent.access.grants

        # Find the grant for our test user
        user = accounts.datastore.get_user(test_email)
        found_grant = False
        for grant in grants:
            if grant.subject_type == "user" and grant.subject_id == str(user.id):
                found_grant = True
                assert grant.permission == "manage"
                break

        assert found_grant, f"Grant not found for user {test_email}"

        # Clean up
        records_service.delete_record(identity, record_id, data=tombstone)


@pytest.mark.integration
def test_add_editor_with_permission(
    app, minimal_record, identity, records_service, tombstone
):
    """Test add_editor command with different permission level."""
    from cca.scripts.add_editor import add_editor
    from click.testing import CliRunner
    from invenio_accounts import current_accounts as accounts

    runner = CliRunner()
    test_email = "viewer-test@example.com"

    with app.app_context():
        # Create user
        user = accounts.datastore.get_user(test_email)
        if not user:
            accounts.datastore.create_user(
                email=test_email,
                username="viewertest",
                password="ViewerPass123!",
                active=True,
            )
            accounts.datastore.commit()

        # Create record
        draft = records_service.create(identity, minimal_record)
        record = records_service.publish(identity, draft.id)
        record_id = record.id

        # Add as preview editor
        result = runner.invoke(
            add_editor, [record_id, test_email, "--permission", "preview"]
        )

        assert result.exit_code == 0
        assert "preview" in result.output

        # Verify permission level
        record_item = records_service.read(identity, id_=record_id)
        parent = record_item._record.parent
        user = accounts.datastore.get_user(test_email)

        for grant in parent.access.grants:
            if grant.subject_type == "user" and grant.subject_id == str(user.id):
                assert grant.permission == "preview"
                break

        # Clean up
        records_service.delete_record(identity, record_id, data=tombstone)


@pytest.mark.integration
def test_add_editor_nonexistent_user(
    app, minimal_record, identity, records_service, tombstone
):
    """Test add_editor command fails gracefully for non-existent user."""
    from cca.scripts.add_editor import add_editor
    from click.testing import CliRunner

    runner = CliRunner()

    with app.app_context():
        # Create record
        draft = records_service.create(identity, minimal_record)
        record = records_service.publish(identity, draft.id)
        record_id = record.id

        # Try to add non-existent user
        result = runner.invoke(add_editor, [record_id, "nonexistent@example.com"])

        assert result.exit_code == 1
        assert "ERROR" in result.output
        assert "no user found" in result.output

        # Clean up
        records_service.delete_record(identity, record_id, data=tombstone)


@pytest.mark.unit
def test_id_map_utils_load_save():
    """Test loading and saving id-map.json files."""
    from cca.scripts.id_map_utils import load_id_map, save_id_map

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_data = {
            "https://vault.cca.edu/items/test-123/1/": {
                "id": "abc-xyz",
                "collaborators": ["user1"],
                "events": [{"name": "import", "data": {"id": "abc-xyz"}}],
            }
        }
        json.dump(test_data, f)
        temp_file = Path(f.name)

    try:
        # Test load
        loaded_data = load_id_map(temp_file)
        assert "https://vault.cca.edu/items/test-123/1/" in loaded_data
        assert loaded_data["https://vault.cca.edu/items/test-123/1/"]["id"] == "abc-xyz"

        # Test save
        loaded_data["https://vault.cca.edu/items/test-123/1/"]["id"] = "updated-id"
        save_id_map(temp_file, loaded_data)

        # Verify save
        reloaded_data = load_id_map(temp_file)
        assert (
            reloaded_data["https://vault.cca.edu/items/test-123/1/"]["id"]
            == "updated-id"
        )
    finally:
        temp_file.unlink(missing_ok=True)


@pytest.mark.unit
def test_id_map_utils_record_collaborator_event():
    """Test recording collaborator events in id-map.json."""
    from cca.scripts.id_map_utils import (
        get_entry_by_record_id,
        record_collaborator_event,
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_data = {
            "https://vault.cca.edu/items/test-456/1/": {
                "id": "record-123",
                "collaborators": ["user1"],
                "events": [{"name": "import", "data": {"id": "record-123"}}],
            }
        }
        json.dump(test_data, f)
        temp_file = Path(f.name)

    try:
        # Record a collaborator event
        record_collaborator_event(
            temp_file, "record-123", "user1@example.com", "manage"
        )

        # Verify event was added
        vault_url, entry = get_entry_by_record_id(temp_file, "record-123")
        assert entry is not None
        events = entry["events"]
        assert len(events) == 2  # import + add_collaborator
        collab_event = next(e for e in events if e["name"] == "add_collaborator")
        assert collab_event["data"]["email"] == "user1@example.com"
        assert collab_event["data"]["permission"] == "manage"
        assert "time" in collab_event
    finally:
        temp_file.unlink(missing_ok=True)


@pytest.mark.unit
def test_id_map_utils_pending_collaborators():
    """Test getting pending collaborators from id-map.json."""
    from cca.scripts.id_map_utils import get_pending_collaborators

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_data = {
            "https://vault.cca.edu/items/test-1/1/": {
                "id": "rec-1",
                "title": "Test Record 1",
                "collaborators": ["user1", "user2"],
                "events": [
                    {"name": "import", "data": {"id": "rec-1"}},
                    {
                        "name": "add_collaborator",
                        "data": {"email": "user1@example.com"},
                    },
                ],
            },
            "https://vault.cca.edu/items/test-2/1/": {
                "id": "rec-2",
                "title": "Test Record 2",
                "collaborators": ["user3"],
                "events": [{"name": "import", "data": {"id": "rec-2"}}],
            },
            "https://vault.cca.edu/items/test-3/1/": {
                "id": "rec-3",
                "title": "Test Record 3",
                "collaborators": [],
                "events": [{"name": "import", "data": {"id": "rec-3"}}],
            },
        }
        json.dump(test_data, f)
        temp_file = Path(f.name)

    try:
        pending = get_pending_collaborators(temp_file)

        # Should have 2 records with pending collaborators
        assert len(pending) == 2

        # rec-1 has user2 pending (user1 has event)
        rec1 = next(p for p in pending if p["record_id"] == "rec-1")
        assert rec1["collaborators"] == ["user2"]

        # rec-2 has user3 pending
        rec2 = next(p for p in pending if p["record_id"] == "rec-2")
        assert rec2["collaborators"] == ["user3"]

        # rec-3 should not be in pending (no collaborators)
        assert not any(p["record_id"] == "rec-3" for p in pending)
    finally:
        temp_file.unlink(missing_ok=True)


@pytest.mark.integration
def test_add_editor_with_map_file(
    app, minimal_record, identity, records_service, tombstone
):
    """Test add_editor command with --map-file option."""
    from cca.scripts.add_editor import add_editor
    from cca.scripts.id_map_utils import get_entry_by_record_id
    from click.testing import CliRunner
    from invenio_accounts import current_accounts as accounts

    runner = CliRunner()
    test_email = "mapuser@example.com"

    with app.app_context():
        # Create user
        user = accounts.datastore.get_user(test_email)
        if not user:
            accounts.datastore.create_user(
                email=test_email,
                username="mapuser",
                password="MapPass123!",
                active=True,
            )
            accounts.datastore.commit()

        # Create record
        draft = records_service.create(identity, minimal_record)
        record = records_service.publish(identity, draft.id)
        record_id = record.id

        # Create map file with this record
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = {
                "https://vault.cca.edu/items/test/1/": {
                    "id": record_id,
                    "collaborators": ["mapuser"],
                    "events": [{"name": "import", "data": {"id": record_id}}],
                }
            }
            json.dump(test_data, f)
            map_file = Path(f.name)

        try:
            # Add editor with map file
            result = runner.invoke(
                add_editor,
                [record_id, test_email, "--map-file", str(map_file)],
            )

            assert result.exit_code == 0
            assert "Recorded event" in result.output

            # Verify event was recorded in map file
            vault_url, entry = get_entry_by_record_id(map_file, record_id)
            assert entry is not None
            events = entry["events"]
            assert len(events) == 2  # import + add_collaborator
            collab_event = next(e for e in events if e["name"] == "add_collaborator")
            assert collab_event["data"]["email"] == test_email

            # Clean up
            records_service.delete_record(identity, record_id, data=tombstone)
        finally:
            map_file.unlink(missing_ok=True)


@pytest.mark.integration
def test_add_editor_batch_mode(
    app, minimal_record, identity, records_service, tombstone
):
    """Test add_editor command in batch mode with --map-file."""
    from cca.scripts.add_editor import add_editor
    from cca.scripts.id_map_utils import get_pending_collaborators
    from click.testing import CliRunner
    from invenio_accounts import current_accounts as accounts

    runner = CliRunner()

    with app.app_context():
        # Create test users
        for username in ["batchuser1", "batchuser2"]:
            email = f"{username}@cca.edu"
            if not accounts.datastore.get_user(email):
                accounts.datastore.create_user(
                    email=email,
                    username=username,
                    password="BatchPass123!",
                    active=True,
                )
        accounts.datastore.commit()

        # Create two test records
        draft1 = records_service.create(identity, minimal_record)
        record1 = records_service.publish(identity, draft1.id)

        minimal_record2 = minimal_record.copy()
        minimal_record2["metadata"]["title"] = "Test Record 2"
        draft2 = records_service.create(identity, minimal_record2)
        record2 = records_service.publish(identity, draft2.id)

        # Create map file with pending collaborators
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = {
                "https://vault.cca.edu/items/test1/1/": {
                    "id": record1.id,
                    "title": "Test Record 1",
                    "collaborators": ["batchuser1"],
                    "events": [{"name": "import", "data": {"id": record1.id}}],
                },
                "https://vault.cca.edu/items/test2/1/": {
                    "id": record2.id,
                    "title": "Test Record 2",
                    "collaborators": ["batchuser2"],
                    "events": [{"name": "import", "data": {"id": record2.id}}],
                },
            }
            json.dump(test_data, f)
            map_file = Path(f.name)

        try:
            # Verify we have pending collaborators
            pending = get_pending_collaborators(map_file)
            assert len(pending) == 2

            # Run batch mode
            result = runner.invoke(add_editor, ["--map-file", str(map_file)])

            assert result.exit_code == 0
            assert "Found 2 records" in result.output
            assert "batchuser1@cca.edu" in result.output
            assert "batchuser2@cca.edu" in result.output
            assert "2 collaborators added" in result.output

            # Verify no more pending collaborators
            pending_after = get_pending_collaborators(map_file)
            assert len(pending_after) == 0

            # Clean up
            records_service.delete_record(identity, record1.id, data=tombstone)
            records_service.delete_record(identity, record2.id, data=tombstone)
        finally:
            map_file.unlink(missing_ok=True)
