# [Custom Code](https://inveniordm.docs.cern.ch/operate/code/custom_code/) & Views

The "site" folder is like our own custom Invenio module. Right now, everything in here is mostly a demo or experiment.

We have several custom CLI commands nested under `invenio cca`.

## Add Users

Use a JSON file to bulk create user accounts.

```sh
Usage: invenio cca add-users [OPTIONS]

  Add user accounts to Invenio. Automatically activates & confirms the
  accounts. To update the names vocabulary, see `invenio vocabularies update
  -v names`.

Options:
  -h, --help       Show this message and exit.
  -f, --file PATH  JSON file of users.
  --reindex        Reindex afterwards (runs invenio rdm rebuild-all-indices -o
                   users)
```

See [the test_users.json](../app_data/test_users.json) for the expected data format.

## Courses Data

Run `uv run invenio cca courses-index` to download courses JSON data and add it to a `courses` OpenSearch index.

```sh
Usage: invenio cca courses-index [OPTIONS]

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
uv run invenio cca groups-sync --employees --create-groups --dry-run
# Real run students (downloads and executes invenio commands):
uv run invenio cca groups-sync --students --create-groups --reindex
```

If we only want students or employees, pass `--students` or `--employees` respectively. Use `--create-groups` to run `invenio roles create ...` before adding members. Use `--reindex` to rebuild group indices after updates.

The script expects both JSON files to be in our typical Workday format; an object containg a `Report_Entry` array of people objects. Student objects should have an `inst_email` and a `programs` array. Employee objects should have `work_email` and `program`.

### Testing groups_sync.py

There are pytest unit tests for the groups sync helpers at `tests/test_groups_sync.py`. Run tests from the repository root:

```sh
uv run pytest
```

The tests mock command execution and validate that the correct `invenio` commands would be produced for sample input.

## Add Editor

Add user(s) as editor(s) to record(s). Supports two modes:

1. **Single mode**: Add one user to one record
2. **Batch mode**: Process all pending collaborators from a migration id-map file

```sh
Usage: invenio cca add-editor [OPTIONS] [RECORD_ID] [EMAIL]

  Add user(s) as editor(s) to record(s).

  Single record mode (record_id and email required):
    Adds one user to one record, optionally recording in id-map.

  Batch mode (--map-file required, no record_id/email):
    Processes all records in the id-map that have collaborators listed but
    no corresponding add_collaborator event. Looks up user emails by username.

  Examples:
    # Single mode
    invenio cca add-editor abc12-xyz34 user@example.com
    invenio cca add-editor abc12-xyz34 user@example.com --permission edit

    # Batch mode - process all pending collaborators
    invenio cca add-editor --map-file migration/id-map.json

Options:
  --permission [view|preview|edit|manage]
                                  Permission level to grant (default: manage)
  --map-file PATH                 Path to id-map.json file; processes all
                                  pending collaborators if no record_id given
  -h, --help                      Show this message and exit.
```

### Batch Mode and ID Maps

During migration from VAULT, the `id-map.json` tracks which records have been imported and which collaborators need to be added. The file structure looks like:

```json
{
  "https://vault.cca.edu/items/UUID/VERSION/": {
    "id": "new-invenio-id",
    "collaborators": ["username1", "username2"],
    "events": [
      {"name": "import", "data": {...}, "time": "..."},
      {"name": "add_collaborator", "data": {"email": "user@..."}, "time": "..."}
    ]
  }
}
```

Batch mode processes id map entries with `collaborators` that don't have a corresponding `add_collaborator` event. It attempts to find users by their username, trying both the exact value and `{username}@cca.edu`. When a collaborator is successfully added, an event is recorded in the map file.

See [site/cca/scripts/id_map_utils.py](./cca/scripts/id_map_utils.py) for utility functions to work with the id map programmatically.

## Set Owner

Set the owner of record(s). Supports two modes:

1. **Single mode**: Set owner of one record
2. **Batch mode**: Process all pending owners from a migration id-map file

```sh
Usage: invenio cca set-owner [OPTIONS] [RECORD_ID] [EMAIL]

  Set the owner of record(s).

  Single record mode (record_id required):
    Sets owner to the provided email or, if no email given, to the email
    of the first creator in the metadata.

  Batch mode (--map-file required, no record_id):
    Processes all records in the id-map that have an owner listed but
    no corresponding set_owner event.

  Examples:
    # Set owner from creator metadata
    invenio cca set-owner abc12-xyz34

    # Set owner to specific email
    invenio cca set-owner abc12-xyz34 user@example.com

    # Batch mode - process all pending owners
    invenio cca set-owner --map-file migration/id-map.json

Options:
  --map-file PATH  Path to id-map.json file; processes all pending owners if
                   no record_id given
  -h, --help       Show this message and exit.
```

### Batch Mode for Owners

Similar to `add-editor`, batch mode processes records that have an `owner` field in the id-map but no `set_owner` event recorded. The command looks up owners by username (trying both the exact value and `{username}@cca.edu`) and records a `set_owner` event in the map file when successful.

## Add Communities

Create communities from a YAML file using the REST API.

```sh
Usage: python site/cca/scripts/add_communities.py [OPTIONS]

  Create communities from a YAML file. Requires an Invenio personal access
  token, which it looks for in the TOKEN or INVENIO_TOKEN env vars. The
  domain of the Invenio instance can be specified with the --host flag or
  using HOST or INVENIO_HOST env vars.

Options:
  -h, --help            Show this message and exit.
  -f, --file PATH       YAML file of communities (default:
                        app_data/communities.yaml).
  --host TEXT           Hostname of Invenio instance (e.g. invenio-
                        dev.cca.edu)
  -n, --no-verify       Disable SSL verification (use during local testing).
  -t, --token TEXT      Administrator personal access token.
```

See [the communities.yaml](../app_data/communities.yaml) for the expected data format. Since this uses the REST API to create communities, it does not need to be run in the Flask app context and thus is not available under the `invenio cca` commands.

## Creating New CLI Commands

- Create file under site/cca/scripts with a typical `@click.command` function. Give the function a meaningful name and not `main`
- In site/cca/cli.py import the command function and `cca.add_command(function_name)`
- The command becomes available under `uv run invenio cca function-name`

This works because of pyproject.toml and site/setup.cfg configuration.
