"""Tests for custom fields configuration.
See also: test_records.test_create_record_with_archives_series
Do these need @pytest.mark.slow? Takes 10+ seconds to run, I guess because of imports."""

import pytest
from cca.customfields import (
    RDM_CUSTOM_FIELDS,
    RDM_CUSTOM_FIELDS_UI,
    RDM_NAMESPACES,
    ArchivesSeriesCF,
)


@pytest.mark.unit
def test_archives_series_custom_field_defined(app):
    """Test that the archives_series custom field is properly defined."""
    # Find the archives_series field
    archives_field = None
    for field in RDM_CUSTOM_FIELDS:
        if hasattr(field, "name") and field.name == "cca:archives_series":
            archives_field = field
            break

    assert archives_field is not None, "archives_series custom field not found"
    assert archives_field.name == "cca:archives_series"


@pytest.mark.unit
def test_archives_series_mapping(app):
    """Test that archives_series has proper search mapping."""
    archives_field = None
    for field in RDM_CUSTOM_FIELDS:
        if hasattr(field, "name") and field.name == "cca:archives_series":
            archives_field = field
            break

    assert archives_field is not None
    mapping = archives_field.mapping
    assert mapping is not None
    assert "properties" in mapping
    assert "series" in mapping["properties"]
    assert "subseries" in mapping["properties"]


@pytest.mark.unit
def test_archives_series_ui_config(app):
    """Test that archives_series has UI configuration."""
    # Find CCA Fields section
    cca_section = None
    for section in RDM_CUSTOM_FIELDS_UI:
        if isinstance(section, dict) and section.get("section") == "CCA Fields":
            cca_section = section
            break

    assert cca_section is not None, "CCA Fields section not found in UI config"
    assert "fields" in cca_section

    # Find archives_series field
    archives_ui_field = None
    for field in cca_section["fields"]:
        if field.get("field") == "cca:archives_series":
            archives_ui_field = field
            break

    assert archives_ui_field is not None, "archives_series not found in UI config"
    assert archives_ui_field["template"] == "archivesseries.html"
    assert archives_ui_field["ui_widget"] == "ArchivesSeries"
    assert "props" in archives_ui_field


@pytest.mark.unit
def test_journal_fields_included(app):
    """Test that journal custom fields are included."""
    # Should have journal fields for OA & DBR records
    field_names = [getattr(f, "name", None) for f in RDM_CUSTOM_FIELDS]

    # Check for journal-related fields
    # The exact field names depend on JOURNAL_CUSTOM_FIELDS
    assert len(field_names) > 1, "Should have multiple custom fields"
    assert "cca:archives_series" in field_names


@pytest.mark.unit
def test_cca_namespace_defined(app):
    """Test that CCA namespace is properly defined."""
    assert "cca" in RDM_NAMESPACES
    assert RDM_NAMESPACES["cca"] == "https://libraries.cca.edu/"


@pytest.mark.unit
def test_archives_series_field_structure():
    """Test the ArchivesSeriesCF class structure."""
    field = ArchivesSeriesCF(name="test:archives")

    # Should have required properties
    assert hasattr(field, "field")
    assert hasattr(field, "mapping")
    assert field.name == "test:archives"

    # Mapping should have correct structure
    mapping = field.mapping
    assert "properties" in mapping
    assert "series" in mapping["properties"]
    assert "subseries" in mapping["properties"]
    assert mapping["properties"]["series"]["type"] == "text"
    assert mapping["properties"]["subseries"]["type"] == "text"
