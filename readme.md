# CCA InvenioRDM

CCA InvenioRDM instance. This is mostly a cookiecutter Invenio project with some custom settings and vocabularies. See our "notes" folder for further documentation.

## Setup

Development requires docker, python, uv, node, and ImageMagick. `invenio-cli check-requirements --development` checks these requirements. See [our mise.toml](mise.toml) file; mise isn't required, but is helpful. To install on an M2 Mac, additional packages are needed: `brew install cairo libffi libxmlsec1 pkg-config`. See [build.md](./notes/build.md) for notes on overcoming build errors.

Many configuration values are in Secret Manager; see [configure.md](./notes/configure.md#secret-manager) for details.

Some fixtures are not in this repository. Build them with the tools in [the vault_migration repository](https://github.com/cca/vault_migration) and copy them here.

```sh
# in vault_migration
gsutil cp gs://integration-success/employee_data.json employee_data.json
gsutil cp gs://integration-success/student_data.json student_data.json
uv run python taxos/users.py employee_data.json student_data.json
INVENIO_REPO=/path/to/this/repo ./vocab/sync # copies to this repo
```

Then run the commands below from the root of this project to install the app:

```sh
uv tool install invenio-cli # install invenio-cli globally (recommended instead of using pip)
invenio-cli install all --dev # creates the virtualenv, install dependencies, & other setup
invenio-cli services setup --no-demo-data # sets up db, cache, search, task queue
export ENVIRONMENT=local # if not using `mise` ensure vars from .env exist
invenio-cli run # runs the application & celery worker for the task queue
```

The services setup enqueues many tasks rather than completing them synchronously, so the first time you `run` the app it takes a while before setup is complete.

## Overview

Following is an overview of the generated files and folders:

| Name | Description |
|---|---|
| `Dockerfile` | Dockerfile used to build your application image. |
| `pyproject.toml` | Python dependency requirements |
| `uv.lock` | Locked requirements |
| `app_data` | Application data such as vocabularies. |
| `assets` | Web assets (CSS, JavaScript, LESS, JSX templates) used in the Webpack build. |
| `docker` | Example configuration for NGINX, Postgres Admin, and uWSGI. |
| `docker-compose.full.yml` | Example of a full infrastructure stack. |
| `docker-compose.yml` | Backend services needed for local development. |
| `docker-services.yml` | Common services for the Docker Compose files. |
| `invenio.cfg` | Main configuration file. |
| `logs` | Log files. |
| `notes` | CCA's documentation on running & developing the app. |
| `site` | [Custom site code](https://inveniordm.docs.cern.ch/develop/howtos/custom_code/) and modules. |
| `static` | Static files that need to be served as-is (e.g. images). |
| `templates` | Folder for your Jinja templates. |
| `.invenio` | Common file used by Invenio-CLI to be version controlled. |
| `.invenio.private` | Private file used by Invenio-CLI *not* version controlled. |
| `.env`, `example.env` | Environment variables automatically loaded with `dotenv` |
| `mise.toml` | [mise](https://mise.jdx.dev/) manages env vars & installed languages (node, python) |

## Documentation

See the [InvenioRDM Documentation](https://inveniordm.docs.cern.ch/) for general details and [our notes](./notes/) for more specifics.

## LICENSE

[ECL 2.0](https://opensource.org/license/ecl-2-0)
