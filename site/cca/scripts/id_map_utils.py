"""Utilities for working with id-map.json files during migrations.

The id-map.json file tracks mappings between old VAULT URLs and new Invenio record IDs,
along with metadata about the migration process such as collaborators that need to be
added as editors.

Structure:
{
  "https://vault.cca.edu/items/UUID/VERSION/": {
    "id": "new-invenio-id",
    "collaborators": ["user1", "user2"],
    "events": [
      {"name": "import", "data": {...}, "time": "..."},
      {"name": "add_collaborator", "data": {"email": "user1@..."}, "time": "..."}
    ],
    ...
  }
}
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_id_map(map_file: str | Path) -> dict[str, Any]:
    """Load the id-map.json file.

    Args:
        map_file: Path to the id-map.json file

    Returns:
        Dictionary containing the ID mappings (keyed by old VAULT URLs)

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    path: Path = Path(map_file)
    with path.open("r") as f:
        return json.load(f)


def save_id_map(map_file: str | Path, data: dict[str, Any]) -> None:
    """Save the id-map.json file.

    Args:
        map_file: Path to the id-map.json file
        data: Dictionary to save

    Raises:
        OSError: If the file cannot be written
    """
    path: Path = Path(map_file)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def get_entry_by_record_id(
    map_file: str | Path, record_id: str
) -> tuple[str | None, dict[str, Any] | None]:
    """Get the map entry for a specific Invenio record ID.

    Args:
        map_file: Path to the id-map.json file
        record_id: The new Invenio record ID

    Returns:
        The entry_dict or None if not found
    """
    data: dict[str, Any] = load_id_map(map_file)
    for url, entry in data.items():
        if entry.get("id") == record_id:
            return url, entry
    return (None, None)


def record_event(
    map_file: str | Path,
    record_id: str,
    event_name: str,
    event_data: dict[str, Any],
) -> None:
    """Record an event for a record in the id-map.

    Adds an event to the events array for the record to track operations
    performed on it in Invenio.

    Args:
        map_file: Path to the id-map.json file
        record_id: The new Invenio record ID
        event_name: Name of the event (e.g., "add_collaborator", "set_owner")
        event_data: Dictionary of event-specific data

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the record is not found in the map
        json.JSONDecodeError: If the file is not valid JSON
        OSError: If the file cannot be written
    """
    vault_url, entry = get_entry_by_record_id(map_file, record_id)
    if entry is None or vault_url is None:
        raise ValueError(f"Record {record_id} not found in id-map")

    data: dict[str, Any] = load_id_map(map_file)

    # Ensure events array exists
    if "events" not in entry:
        entry["events"] = []

    # Add the event
    event: dict[str, Any] = {
        "name": event_name,
        "data": event_data,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    entry["events"].append(event)

    # Update the entry in the data
    data[vault_url] = entry
    save_id_map(map_file, data)


def has_collaborator_event(entry: dict[str, Any], collaborator: str) -> bool:
    """Check if a collaborator has an add_collaborator event.

    Args:
        entry: The map entry dictionary
        collaborator: The collaborator username or email to check

    Returns:
        True if an add_collaborator event exists for this collaborator
    """
    events: list[dict[str, Any]] = entry.get("events", [])
    for event in events:
        if event.get("name") == "add_collaborator":
            event_email = event.get("data", {}).get("email", "")
            # Check if email matches or is contained in the collaborator string
            if event_email == collaborator or collaborator in event_email:
                return True
    return False


def get_pending_collaborators(map_file: str | Path) -> list[dict[str, Any]]:
    """Get all records with collaborators that haven't been added yet.

    Returns a list of records that have collaborators listed but no
    corresponding add_collaborator event.

    Args:
        map_file: Path to the id-map.json file

    Returns:
        List of dicts with keys: record_id, collaborators (list of usernames)

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    data: dict[str, Any] = load_id_map(map_file)
    pending: list[dict[str, Any]] = []

    for entry in data.values():
        record_id: str | None = entry.get("id")
        collaborators: list[str] = entry.get("collaborators", [])

        if not record_id or not collaborators:
            continue

        # Find collaborators without events
        pending_collabs: list[str] = [
            collab
            for collab in collaborators
            if not has_collaborator_event(entry, collab)
        ]

        if pending_collabs:
            pending.append(
                {
                    "record_id": record_id,
                    "collaborators": pending_collabs,
                    "title": entry.get("title", ""),
                }
            )

    return pending


def has_owner_event(entry: dict[str, Any]) -> bool:
    """Check if a record has a set_owner event.

    Args:
        entry: The map entry dictionary

    Returns:
        True if a set_owner event exists for this record
    """
    events: list[dict[str, Any]] = entry.get("events", [])
    for event in events:
        if event.get("name") == "set_owner":
            return True
    return False


def get_pending_owners(map_file: str | Path) -> list[dict[str, Any]]:
    """Get all records with owners that haven't been set yet.

    Returns a list of records that have an owner listed but no
    corresponding set_owner event.

    Args:
        map_file: Path to the id-map.json file

    Returns:
        List of dicts with keys: record_id, owner (email or username), title

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    data: dict[str, Any] = load_id_map(map_file)
    pending: list[dict[str, Any]] = []

    for entry in data.values():
        record_id: str | None = entry.get("id")
        owner: str | None = entry.get("owner")

        if not record_id or not owner:
            continue

        # Check if owner has been set
        if not has_owner_event(entry):
            pending.append(
                {
                    "record_id": record_id,
                    "owner": owner,
                    "title": entry.get("title", ""),
                }
            )

    return pending
