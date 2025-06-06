# usage: python upload_courses.py <bucket_name> <source_blob_name> <destination_file_name> <os_host>
from datetime import date
import json
import os
from typing import Any

import click
from google.cloud import storage
from opensearchpy import OpenSearch, helpers


def current_term() -> str:
    """Returns the current semester in the form it's used in the courses JSON
    filename, e.g. "Fall_2025".
    """
    today: date = date.today()
    year: int = today.year

    if today.month >= 8:
        season = "Fall"
    elif today.month >= 5:
        season = "Summer"
    else:
        season = "Spring"

    return f"{season}_{year}"


def download_courses(
    bucket_name: str,
    filename: str,
    destination_filename: str,
):
    """Download courses JSON from a Google Cloud Storage bucket."""
    # TODO authentication
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.download_to_filename(destination_filename)
    print(f"Downloaded {filename} to {destination_filename}.")


def prepare_bulk_data(file_path):
    """Prepare data for OpenSearch bulk indexing."""
    with open(file_path, "r") as f:
        courses: list[dict[str, Any]] = json.load(f)

    bulk_data: list[dict[str, Any]] = []
    for course in courses:
        bulk_data.append(
            # We want this to KeyError if a course lacks an id
            {"_index": "courses", "_id": course["section_refid"], "_source": course}
        )
    return bulk_data


def push_to_opensearch(os_host, bulk_data):
    """Push bulk data to OpenSearch."""
    # TODO presumably will need to set up authentication
    os_client = OpenSearch([os_host])
    helpers.bulk(os_client, bulk_data)
    print(f"Successfully indexed {len(bulk_data)} documents into OpenSearch.")


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "--bucket",
    default=lambda: os.getenv("COURSES_BUCKET_NAME", "int_files_source"),
    help="The name of the Google Cloud Storage bucket.",
)
@click.option(
    "--filename",
    default=lambda: os.getenv(
        "COURSES_SOURCE_BLOB_NAME", f"course_section_data_AP_{current_term()}.json"
    ),
    help="The name of the source blob in the bucket.",
)
@click.option(
    "--destination-filename",
    default=lambda: os.getenv("COURSES_DESTINATION_FILE_NAME", "courses.json"),
    help="Local file name of the downloaded JSON.",
)
@click.option(
    "--os-host",
    default=lambda: os.getenv("COURSES_OS_HOST", "http://localhost:9200"),
    help="The OpenSearch host URL.",
)
def main(bucket: str, filename: str, destination_filename: str, os_host: str):
    """Download course JSON from the Integrations bucket, format it for bulk addition to OpenSearch, and push it to the "courses" index. By default, the bucket name is "int_files_source", the blob name is "course_section_data_AP_<current_term>.json", and the OpenSearch host is "http://localhost:9200"."""
    download_courses(bucket, filename, destination_filename)
    bulk_data: list[dict[str, Any]] = prepare_bulk_data(destination_filename)
    push_to_opensearch(os_host, bulk_data)


if __name__ == "__main__":
    main()
