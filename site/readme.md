# Custom Code & Views

The "site" folder is like our own custom Invenio module. Right now, everything in here is mostly a demo or experiment.

https://inveniordm.docs.cern.ch/develop/howtos/custom_code/

## Courses Data

Run `uv run python site/cca/cli.py` to download courses JSON data and add it to a `courses` OpenSearch index.

```sh
Usage: cli.py [OPTIONS]

  Download course JSON from the Integrations bucket, format it for bulk
  addition to OpenSearch, and push it to the "courses" index. By default, the
  bucket name is "int_files_source", the blob name is
  "course_section_data_AP_<current_term>.json", and the OpenSearch host is
  "http://localhost:9200".

Options:
  -h, --help                   Show this message and exit.
  --bucket TEXT                The name of the Google Cloud Storage bucket.
  --filename TEXT              The name of the source blob in the bucket.
  --destination-filename TEXT  Local file name of the downloaded JSON.
  --os-host TEXT               The OpenSearch host URL.
  --delete                     Delete the local course file afterwards
```

## Groups Sync (students & employees)

There is a CLI to sync students and employees into Invenio role groups: `site/cca/scripts/groups_sync.py`. Usage:

```sh
# Dry-run faculty (prints commands, does not download or execute)
uv run python site/cca/scripts/groups_sync.py --employees --create-groups --dry-run
# Real run students (downloads and executes invenio commands):
uv run python site/cca/scripts/groups_sync.py --students --create-groups --reindex
```

If we only want students or employees, pass `--students` or `--employees` respectively. Use `--create-groups` to run `invenio roles create ...` before adding members. Use `--reindex` to rebuild group indices after updates.

The script expects both JSON files to be in our typical Workday format; an object containg a `Report_Entry` array of people objects. Student objects should have an `inst_email` and a `programs` array. Employee objects should have `work_email` and `program`.

### Testing groups_sync.py

There are pytest unit tests for the groups sync helpers at `tests/test_groups_sync.py`. Run tests from the repository root:

```sh
uv run pytest -q
```

The tests mock command execution and validate that the correct `invenio` commands would be produced for sample input.
