# CCA InvenioRDM

CCA InvenioRDM instance. This is mostly a cookiecutter Invenio project with some custom settings and vocabularies. See our "notes" folder for further documentation.

## Setup

Requires Docker, python 3.9, pipenv, node 16, and npm 7. `invenio-cli check-requirements --development` will check if you have these. To install on an M2 Mac, additional packages are needed: `brew install cairo libffi pkg-config`. Finally, the invenio-saml module also requires `brew install libxmlsec1`.

Some fixtures are not checked into this repository. Build them with the tools in the cca/vault_migration repository and copy them here.

```sh
# in vault_migration
gsutil cp gs://BUCKET/employee_data.json employee_data.json
gsutil cp gs://BUCKET/student_data.json student_data.json
pipenv run python taxos/users.py employee_data.json student_data.json
INVENIO_REPO=/path/to/this/repo ./vocab/sync # copies updated vocabs to this repo
```

Then run the commands below from the root of this project to install the app:

```sh
pipx install invenio-cli # install invenio-cli globally (recommend using pipx instead of pip)
invenio-cli install --dev # creates the virtualenv, install dependencies, & some other setup
invenio-cli services setup --no-demo-data # sets up db, cache, search, task queue
invenio-cli run # runs the application
```

The services setup enqueues many tasks rather than completing them synchronously, so the first time you `run` the app it will take a while before setup is complete.

I've run into `invenio-cli install` build errors related to the cairo package, the errors say something like "no library called "cairo" was found" and "cannot load library 'libcairo.2.dylib'". I had cairo installed via homebrew, but the library wasn't in any of the directories that the build process was looking in. I fixed this with `cp /opt/homebrew/Cellar/cairo/1.18.0/lib/libcairo.2.dylib /usr/local/lib/` (the path to the cairo library may be different on your system).

## Overview

Following is an overview of the generated files and folders:

| Name | Description |
|---|---|
| `Dockerfile` | Dockerfile used to build your application image. |
| `Pipfile` | Python requirements installed via [pipenv](https://pipenv.pypa.io) |
| `Pipfile.lock` | Locked requirements (generated on first install). |
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

## Documentation

To learn how to configure, customize, deploy and much more, visit the [InvenioRDM Documentation](https://inveniordm.docs.cern.ch/).
