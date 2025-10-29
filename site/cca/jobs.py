from invenio_jobs.jobs import JobType, PredefinedArgsSchema
from marshmallow import fields

from cca.tasks import test_task


class TestJobArgsSchema(PredefinedArgsSchema):
    # required=False is apparently not enough to make optional in UI
    dry_run = fields.Boolean(
        allow_none=True,
        dump_default=False,
        load_default=False,
        metadata={
            "description": "If true, no changes will be persisted.",
            # title is sentenced-cased so "Run" is not capitalized
            "title": "Dry Run",
        },
        required=False,
    )
    job_arg_schema = fields.String(
        dump_default="TestJobArgsSchema",
        load_default="TestJobArgsSchema",
        metadata={"type": "hidden"},
    )
    msg = fields.String(
        allow_none=True,
        dump_default="",
        load_default="",
        metadata={"description": "Message to print.", "title": "Message"},
        required=False,
    )


class TestJob(JobType):
    id: str = "test_task"
    title: str = "Test Task"
    description: str = "Print message and time since last ran."
    task = test_task
    arguments_schema = TestJobArgsSchema

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        return {
            "since": since,
            "dry_run": kwargs.get("dry_run", False),
            "msg": kwargs.get("msg", ""),
        }
