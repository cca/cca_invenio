import importlib.util
import pathlib
import sys
from typing import Any

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

gs = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[spec.name] = gs  # type: ignore[attr-defined]
spec.loader.exec_module(gs)  # type: ignore[attr-defined]


def test_slugify_examples():
    assert gs.slugify("Fine Art") == "fine_art"
    assert gs.slugify("CS&IT") == "cs_it"
    assert gs.slugify("") == "unnamed"
    assert gs.slugify("  A  B  ") == "a_b"


def test_process_students_and_employees(monkeypatch):
    calls = []

    def fake_run_cmd(cmd, dry_run):
        # record the command (list form) and dry_run flag
        calls.append((tuple(cmd), bool(dry_run)))

    monkeypatch.setattr(gs, "run_cmd", fake_run_cmd)

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

    gs.process_students(students, create_groups=True, dry_run=False)

    # flatten commands for easier assertions
    cmds = [c for c, _ in calls]

    assert (
        tuple(
            [
                "invenio",
                "roles",
                "create",
                "architecture_majors",
                "-d",
                "Architecture Majors",
            ]
        )
        in cmds
    )
    assert (
        tuple(["invenio", "roles", "add", "s1@cca.edu", "architecture_majors"]) in cmds
    )
    assert (
        tuple(["invenio", "roles", "create", "design_majors", "-d", "Design Majors"])
        in cmds
    )
    assert tuple(["invenio", "roles", "add", "s2@cca.edu", "design_majors"]) in cmds
    # double major tests
    assert (
        tuple(
            ["invenio", "roles", "create", "painting_majors", "-d", "Painting Majors"]
        )
        in cmds
    )
    assert (
        tuple(["invenio", "roles", "create", "drawing_majors", "-d", "Drawing Majors"])
        in cmds
    )
    assert tuple(["invenio", "roles", "add", "s6@cca.edu", "painting_majors"]) in cmds
    assert tuple(["invenio", "roles", "add", "s6@cca.edu", "drawing_majors"]) in cmds

    # Clear and test employees
    calls.clear()

    employees = [
        {"work_email": "f1@cca.edu", "program": "Fine Arts"},
        {"work_email": "f2@cca.edu", "program": "Fine Arts"},
        {"work_email": "no_prog@cca.edu", "program": ""},
        {"work_email": "also_no_prog@cca.edu"},
        {"work_email": None, "program": "Math"},
    ]

    gs.process_employees(employees, create_groups=True, dry_run=False)
    cmds = [c for c, _ in calls]

    assert (
        tuple(
            [
                "invenio",
                "roles",
                "create",
                "fine_arts_faculty",
                "-d",
                "Fine Arts Faculty",
            ]
        )
        in cmds
    )
    assert tuple(["invenio", "roles", "add", "f1@cca.edu", "fine_arts_faculty"]) in cmds
    assert tuple(["invenio", "roles", "add", "f2@cca.edu", "fine_arts_faculty"]) in cmds
