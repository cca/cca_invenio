"""Testing utilities and shared fixtures for InvenioRDM tests."""


def get_tombstone_data(note="Test cleanup"):
    """Return standard tombstone data for test record cleanup.

    Args:
        note: Optional note explaining the deletion reason

    Returns:
        dict: Tombstone data structure for delete_record calls
    """
    return {
        "note": note,
        "is_visible": False,
    }


def wait_for_index(seconds=1):
    """Wait for OpenSearch to index records.

    Args:
        seconds: Number of seconds to wait (default: 1)
    """
    import time

    time.sleep(seconds)
