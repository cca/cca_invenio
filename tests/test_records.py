"""Tests for record creation and management."""

import pytest


@pytest.fixture
def records_service(app):
    """Get records service."""
    from invenio_records_resources.proxies import current_service_registry

    return current_service_registry.get("records")


@pytest.mark.integration
def test_create_minimal_record(
    app, identity, records_service, minimal_record, tombstone
):
    """Test creating a minimal record."""
    # Create draft
    draft = records_service.create(identity, minimal_record)
    assert draft is not None
    assert draft.id is not None
    assert draft["metadata"]["title"] == "Test Record"

    # Publish the record
    record = records_service.publish(identity, draft.id)
    assert record is not None
    assert record["metadata"]["title"] == "Test Record"
    assert record["is_published"] is True

    # Clean up
    records_service.delete_record(identity, record.id, data=tombstone)


@pytest.mark.integration
def test_create_record_with_archives_series(
    app, identity, records_service, record_with_archives_series, tombstone
):
    """Test creating a record with archives_series custom field."""
    # Create draft with custom field
    draft = records_service.create(identity, record_with_archives_series)
    assert draft is not None
    assert "cca:archives_series" in draft["custom_fields"]
    assert (
        draft["custom_fields"]["cca:archives_series"]["series"] == "III. College Life"
    )
    assert draft["custom_fields"]["cca:archives_series"]["subseries"] == "3. Events"

    # Publish the record
    record = records_service.publish(identity, draft.id)
    assert record is not None
    assert "cca:archives_series" in record["custom_fields"]

    # Clean up
    records_service.delete_record(identity, record.id, data=tombstone)


@pytest.mark.integration
def test_update_record(app, identity, records_service, minimal_record, tombstone):
    """Test updating an existing record."""
    # Create and publish
    draft = records_service.create(identity, minimal_record)
    record = records_service.publish(identity, draft.id)

    # Edit the record
    draft = records_service.edit(identity, record.id)
    draft_data = draft.to_dict()
    draft_data["metadata"]["title"] = "Updated Test Record"

    updated_draft = records_service.update_draft(identity, draft.id, draft_data)
    assert updated_draft["metadata"]["title"] == "Updated Test Record"

    # Publish the update
    updated_record = records_service.publish(identity, updated_draft.id)
    assert updated_record["metadata"]["title"] == "Updated Test Record"

    # Clean up
    records_service.delete_record(identity, updated_record.id, data=tombstone)


@pytest.mark.integration
def test_record_with_subjects(
    app, identity, records_service, minimal_record, tombstone
):
    """Test creating a record with subjects."""
    minimal_record["metadata"]["subjects"] = [
        {
            "id": "http://vocab.getty.edu/page/aat/300046300",
            "subject": "Photographs",
            "scheme": "form",
        },
        {
            "id": "http://vocab.getty.edu/page/aat/300123016",
            "subject": "Artists' books",
            "scheme": "form",
        },
    ]

    draft = records_service.create(identity, minimal_record)
    assert len(draft["metadata"]["subjects"]) == 2
    assert any(
        s["id"] == "http://vocab.getty.edu/page/aat/300123016"
        for s in draft["metadata"]["subjects"]
    )

    record = records_service.publish(identity, draft.id)
    assert len(record["metadata"]["subjects"]) == 2

    # Clean up
    records_service.delete_record(identity, record.id, data=tombstone)


@pytest.mark.integration
def test_record_validation_missing_title(app, identity, records_service):
    """Test that record validation catches missing required fields."""
    invalid_record = {
        "metadata": {
            "resource_type": {"id": "image-photograph"},
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "family_name": "Doe",
                        "given_name": "John",
                    }
                }
            ],
            # Missing title
            "publication_date": "2024-01-01",
        }
    }

    with pytest.raises(Exception):  # ValidationError or similar
        records_service.create(identity, invalid_record)
