from datetime import datetime, timedelta, timezone

from celery import shared_task
from flask import current_app as app


@shared_task
def test_task(since: str | None = None, **kwargs):
    # since is passed as a string but is an ISO datetime
    # it is the time _since the last successful run_ not since the last run
    app.logger.info("test task ran")

    if kwargs.get("dry_run"):
        app.logger.info("dry run, nothing will be modified")

    if kwargs.get("msg"):
        app.logger.info(kwargs.get("msg"))

    if since:
        try:
            since_dt: datetime = datetime.fromisoformat(since)
            interval: timedelta = datetime.now(tz=timezone.utc) - since_dt
            app.logger.info(
                f"{round(interval.total_seconds(), 2)} seconds since last run"
            )
        except ValueError:
            app.logger.error(f"invalid 'since' value: {since}")
    else:
        app.logger.info("no 'since' value, mayhaps this is the task's first iteration?")
    # raise invenio_jobs.errors.TaskExecutionPartialError if incomplete
