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


def filter_course_dict(course: dict[str, Any]) -> dict[str, Any]:
    """Return a subset of the course dictionary & improve some fields."""
    course_subset: dict[str, Any] = course.copy()
    # Easiest to define a list of fields we _don't_ want
    unneeded_fields: list[str] = [
        "status",
        "hidden",
        "min_unit",
        "max_unit",
        "grading_basic",
        "capacity",
        "wait_list",
        "enrollment",
        "meetings",
    ]
    for field in unneeded_fields:
        course_subset.pop(field)
    # "AP_Summer_2025" -> "Summer 2025"
    course_subset["term_string"] = (
        course_subset["term"].replace("AP_", "").replace("_", " ")
    )
    # filter out unpublished instructors
    course_subset["instructors"] = [
        instructor
        for instructor in course_subset["instructors"]
        if instructor["published"]
    ]
    course_subset["instructors_string"] = ", ".join(
        [
            f"{instructor['first_name']}{' ' + instructor['middle_name'] + ' ' if instructor['middle_name'] else ' '}{instructor['last_name']}"
            for instructor in course_subset["instructors"]
        ]
    )
    # Make the "owner" academic unit more accessible
    course_subset["owner_program_code"] = [
        au["refid"].replace("AU_", "")
        for au in course_subset["academic_units"]
        if au["course_owner"]
    ][0]
    course_subset["owner_program_name"] = [
        au["name"] for au in course_subset["academic_units"] if au["course_owner"]
    ][0]
    return course_subset


def skip_course(course: dict[str, Any]) -> bool:
    """Return True if the course should be skipped. Skip: 1) hidden, 2) Extension,
    3) Pre-college. Question: do we need to worry about cancelled courses?"""
    if course["hidden"] == "1":
        return True
    # Statuses:
    # Set(4) { 'Closed', 'Open', 'Preliminary', 'Waitlist' }
    owner = [au for au in course["academic_units"] if au["course_owner"]][0]
    if owner["refid"] in ("AU_EXTED", "AU_PRECO"):
        return True
    return False


def prepare_bulk_data(file_path):
    """Prepare data for OpenSearch bulk indexing."""
    with open(file_path, "r") as f:
        courses: list[dict[str, Any]] = json.load(f)
    bulk_data: list[dict[str, Any]] = []
    for course in courses:
        if not skip_course(course):
            course: dict[str, Any] = filter_course_dict(course)
            bulk_data.append(
                # We want this to KeyError if a course lacks an id
                {"_index": "courses", "_id": course["section_refid"], "_source": course}
            )
    return bulk_data


def push_to_opensearch(os_host: str, bulk_data: list[dict[str, Any]]):
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
@click.option(
    "--delete",
    is_flag=True,
    help="Delete the OpenSearch index before pushing new data.",
)
def main(
    bucket: str, filename: str, destination_filename: str, os_host: str, delete: bool
):
    """Download course JSON from the Integrations bucket, format it for bulk addition to OpenSearch, and push it to the "courses" index. By default, the bucket name is "int_files_source", the blob name is "course_section_data_AP_<current_term>.json", and the OpenSearch host is "http://localhost:9200"."""
    if delete:
        os_client = OpenSearch([os_host])
        os_client.indices.delete(
            "courses", allow_no_indices=True, ignore_unavailable=True  # type: ignore
        )
        print("Deleted the 'courses' OpenSearch index.")
    download_courses(bucket, filename, destination_filename)
    bulk_data: list[dict[str, Any]] = prepare_bulk_data(destination_filename)
    push_to_opensearch(os_host, bulk_data)


if __name__ == "__main__":
    main()
