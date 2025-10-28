from invenio_jobs.jobs import JobType, PredefinedArgsSchema
from marshmallow import fields, validate

from cca.tasks import test_task


class TestJobArgsSchema(PredefinedArgsSchema):
    # these are listed as "unknown fields" so something is still wrong
    dry_run = fields.Boolean(
        required=False,
        missing=False,
        metadata={"description": "If true, no changes will be persisted."},
    )
    # msg = fields.String(
    #     required=False, missing=False, metadata={"description": "Message to print."}
    # )


class TestJob(JobType):
    id: str = "test_task"
    title: str = "Test Task"
    description: str = "Print message and time since last ran."
    task = test_task
    arguments_schema = TestJobArgsSchema

    @classmethod
    def build_task_arguments(
        cls, job_obj, since=None, dry_run: bool = False, msg: str = "", **kwargs
    ):
        return {
            "since": since,
            "dry_run": dry_run,
            # "msg": msg
        }
