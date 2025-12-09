import importlib.util
import pathlib
import sys
from typing import Any

import pytest

# Import the module by path so pytest can run from the repo root
MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "site"
    / "cca"
    / "scripts"
    / "groups_sync.py"
)
spec = importlib.util.spec_from_file_location("groups_sync", str(MODULE_PATH))
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load module spec from {MODULE_PATH}")

gs = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gs
spec.loader.exec_module(gs)


@pytest.mark.unit
def test_slugify_examples():
    assert gs.slugify("Fine Art") == "fine_art"
    assert gs.slugify("CS&IT") == "cs_it"
    assert gs.slugify("") == "unnamed"
    assert gs.slugify("  A  B  ") == "a_b"


@pytest.mark.unit
def test_process_students_and_employees(monkeypatch):
    calls: list[tuple] = []

    def fake_create(role, description, ds):
        calls.append(
            (
                "create",
                role,
                description,
            )
        )

    def fake_add(email, role, ds):
        calls.append(
            (
                "add",
                email,
                role,
            )
        )

    monkeypatch.setattr(gs, "create_role", fake_create)
    monkeypatch.setattr(gs, "add_user_to_role", fake_add)

    students: list[dict[str, Any]] = [
        # student with minor/concentration
        {
            "inst_email": "s1@cca.edu",
            "programs": [
                {
                    "program": "Urban Works Concentration",
                    "program_type": "Program Focus",
                },
                {
                    "credentials": "BArch - Bachelor of Architecture",
                    "program": "Architecture",
                    "program_type": "Major",
                },
            ],
        },
        {
            "inst_email": "s2@cca.edu",
            "programs": [
                {
                    "credentials": "Design MBA",
                    "program": "Design",
                    "program_type": "Major",
                },
            ],
        },
        # no programs
        {"inst_email": "s3@cca.edu", "programs": []},
        {"inst_email": "s4@cca.edu"},
        # undeclared
        {
            "inst_email": "s5@cca.edu",
            "programs": [{"program": "Undeclared, UG", "program_type": "Undeclared"}],
        },
        # double major
        {
            "inst_email": "s6@cca.edu",
            "programs": [
                {
                    "credentials": "Painting",
                    "program": "Painting",
                    "program_type": "Major",
                },
                {
                    "credentials": "Drawing",
                    "program": "Drawing",
                    "program_type": "Major",
                },
            ],
        },
    ]

    gs.process_students(students, create_groups=True)

    # flatten commands for easier assertions (calls holds the tuples we need)

    assert ("create", "architecture_majors", "Architecture Majors") in calls
    assert ("add", "s1@cca.edu", "architecture_majors") in calls
    assert ("create", "design_majors", "Design Majors") in calls
    assert ("add", "s2@cca.edu", "design_majors") in calls
    # double major tests
    assert ("create", "painting_majors", "Painting Majors") in calls
    assert ("create", "drawing_majors", "Drawing Majors") in calls
    assert ("add", "s6@cca.edu", "painting_majors") in calls
    assert ("add", "s6@cca.edu", "drawing_majors") in calls

    # Clear and test employees
    calls.clear()

    employees: list[dict[str, Any]] = [
        {"work_email": "f1@cca.edu", "program": "Fine Arts"},
        {"work_email": "f2@cca.edu", "program": "Fine Arts"},
        {"work_email": "no_prog@cca.edu", "program": ""},
        {"work_email": "also_no_prog@cca.edu"},
        {"work_email": None, "program": "Math"},
    ]

    gs.process_employees(employees, create_groups=True)

    assert ("create", "fine_arts_faculty", "Fine Arts Faculty") in calls
    assert ("add", "f1@cca.edu", "fine_arts_faculty") in calls
    assert ("add", "f2@cca.edu", "fine_arts_faculty") in calls
