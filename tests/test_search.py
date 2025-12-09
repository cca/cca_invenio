"""Tests for search functionality."""

import pytest
from invenio_records_resources.proxies import current_service_registry

from tests.utils import get_tombstone_data, wait_for_index


@pytest.fixture
def records_service(app):
    """Get records service."""
    return current_service_registry.get("records")


@pytest.mark.integration
def test_search_all_records(app, identity, records_service):
    """Test searching for all records."""
    results = records_service.search(identity, params={})
    assert results is not None
    assert "hits" in results.to_dict()


@pytest.mark.integration
@pytest.mark.slow
def test_search_by_title(app, identity, records_service, minimal_record):
    """Test searching records by title."""
    # Create a record with unique title
    unique_title = "Unique Test Record for Search 12345"
    minimal_record["metadata"]["title"] = unique_title

    draft = records_service.create(identity, minimal_record)
    record = records_service.publish(identity, draft.id)

    # Search may need time for indexing
    wait_for_index()

    # Search for the record
    results = records_service.search(identity, params={"q": unique_title})
    hits = results.to_dict()["hits"]["hits"]

    # Should find at least our record
    assert len(hits) >= 1
    assert any(h["metadata"]["title"] == unique_title for h in hits)

    # Clean up
    records_service.delete_record(identity, record.id, data=get_tombstone_data())


# ! this test is failing
@pytest.mark.integration
@pytest.mark.slow
def test_search_with_filters(app, identity, records_service, minimal_record):
    """Test searching with resource type filter."""
    # Create a photograph record
    minimal_record["metadata"]["resource_type"] = {"id": "image-photo"}
    draft = records_service.create(identity, minimal_record)
    record = records_service.publish(identity, draft.id)

    wait_for_index()

    # Search with resource type filter
    results = records_service.search(
        identity, params={"q": "resource_type.id:image-photo"}
    )
    hits = results.to_dict()["hits"]["hits"]

    # Should find at least our record
    assert len(hits) >= 1

    # Clean up
    records_service.delete_record(identity, record.id, data=get_tombstone_data())


@pytest.mark.integration
@pytest.mark.slow
def test_search_archives_series(
    app, identity, records_service, record_with_archives_series
):
    """Test searching for records with archives series custom field."""
    # Create record with archives series
    draft = records_service.create(identity, record_with_archives_series)
    record = records_service.publish(identity, draft.id)

    wait_for_index()

    # Search for records with archives series
    # The exact query depends on how the field is indexed
    results = records_service.search(
        identity,
        params={"q": 'custom_fields.cca\\:archives_series.series:"II. College Life"'},
    )
    hits = results.to_dict()["hits"]["hits"]

    # Should find our record
    found = False
    for hit in hits:
        if "cca:archives_series" in hit.get("custom_fields", {}):
            if (
                hit["custom_fields"]["cca:archives_series"]["series"]
                == "II. College Life"
            ):
                found = True
                break

    assert found, "Record with archives series not found in search results"

    # Clean up
    records_service.delete_record(identity, record.id, data=get_tombstone_data())


@pytest.mark.integration
@pytest.mark.slow
def test_search_by_creator(app, identity, records_service, minimal_record):
    """Test searching records by creator name."""
    # Use a unique creator name
    minimal_record["metadata"]["creators"][0]["person_or_org"]["family_name"] = (
        "UniqueLastName123"
    )

    draft = records_service.create(identity, minimal_record)
    record = records_service.publish(identity, draft.id)

    wait_for_index()

    # Search for records by creator
    results = records_service.search(identity, params={"q": "UniqueLastName123"})
    hits = results.to_dict()["hits"]["hits"]

    assert len(hits) >= 1
    assert any("UniqueLastName123" in str(h["metadata"]["creators"]) for h in hits)

    # Clean up
    records_service.delete_record(identity, record.id, data=get_tombstone_data())


@pytest.mark.integration
def test_search_pagination(app, identity, records_service):
    """Test search pagination."""
    # Test with page size
    results = records_service.search(identity, params={"size": 5, "page": 1})
    data = results.to_dict()

    assert "hits" in data
    assert len(data["hits"]["hits"]) <= 5


@pytest.mark.integration
def test_search_sorting(app, identity, records_service):
    """Test search result sorting."""
    # Sort by newest first
    results = records_service.search(identity, params={"sort": "newest"})
    assert results is not None

    # Sort by oldest first
    results = records_service.search(identity, params={"sort": "oldest"})
    assert results is not None
