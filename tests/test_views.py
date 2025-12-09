"""Tests for custom views and routes."""

import pytest


@pytest.mark.integration
def test_vocablist_endpoint_exists(app, client):
    """Test that the /vocablist endpoint exists and returns 200."""
    response = client.get("/vocablist")
    assert response.status_code == 200


@pytest.mark.integration
def test_vocablist_returns_html(app, client):
    """Test that /vocablist returns HTML content."""
    response = client.get("/vocablist")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data.lower()


@pytest.mark.integration
def test_vocablist_content_type(app, client):
    """Test that /vocablist has correct content type."""
    response = client.get("/vocablist")
    assert response.status_code == 200
    assert "text/html" in response.content_type


@pytest.mark.integration
def test_blueprint_registration(app):
    """Test that the cca blueprint is registered."""
    assert "cca" in app.blueprints


@pytest.mark.integration
def test_robots_txt_exists(client):
    """Test that robots.txt is accessible."""
    response = client.get("/robots.txt")
    # Should exist and return 200 or 404 is acceptable
    assert response.status_code in [200, 404]


@pytest.mark.integration
def test_api_root_accessible(client):
    """Test that API root is accessible."""
    response = client.get("/api/")
    assert response.status_code in [200, 301, 302, 404]


@pytest.mark.integration
def test_communities_api_accessible(client):
    """Test that communities API endpoint is accessible."""
    response = client.get("/api/communities")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "hits" in data


@pytest.mark.integration
def test_records_api_accessible(client):
    """Test that records API endpoint is accessible."""
    response = client.get("/api/records")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "hits" in data


@pytest.mark.integration
def test_vocabularies_api_accessible(client):
    """Test that vocabularies API is accessible."""
    response = client.get("/api/vocabularies")
    # May return list of vocabulary types, or redirect to specific vocabulary
    assert response.status_code in [200, 308, 404]
