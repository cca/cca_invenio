from datetime import datetime, timedelta

from celery import shared_task
from flask import current_app as app


@shared_task
# ? do we have to use kwargs or can we add named args here?
def test_task(since: datetime | None = None, **kwargs):
    app.logger.info("test task ran")

    if kwargs.get("dry_run"):
        app.logger.info("dry run, nothing will be modified")

    # if kwargs.get("msg"):
    #     app.logger.info(kwargs.get("msg"))

    if since:
        interval: timedelta = datetime.now() - since
        app.logger.info(f"{interval.total_seconds} seconds since last run")
    else:
        app.logger.info("no 'since' value, mayhaps this is the task's first iteration?")
    # raise invenio_jobs.errors.TaskExecutionPartialError if incomplete
