# CCA InvenioRDM

CCA InvenioRDM instance. This is mostly a cookiecutter Invenio project with additional documentation for us.

## Setup

Requires Docker, python 3.9, pipenv, node, and npm 7. `invenio-cli check-requirements --development` will check if you have all these. To install on an M2 Mac, it seems that additional packages are needed: `brew install cairo libffi pkg-config`.

Finally, the invenio-saml module requires an outdated version of `xmlsec1` which you can't get from homebrew. Eric made a local tap with the requisite version. First, download install Xcode and open it to accept the license agreement. Then `brew tap phette23/local` and `brew install xmlsec1@1.2.37`.

```sh
git clone https://gitlab.com/california-college-of-the-arts/invenio && cd invenio
pip install invenio-cli # install invenio-cli globally
invenio-cli install --dev # creates the virtualenv, install dependencies, & some other setup
invenio-cli services setup --no-demo-data # sets up db, cache, search, task queue
invenio-cli run # runs the application
```

The services setup actually enqueues a many tasks rather than completing them synchronously, so the first time you `run` the app it will take a while before setup is complete.

See our "notes" folder for further documentation.

## Overview

Following is an overview of the generated files and folders:

| Name | Description |
|---|---|
| ``Dockerfile`` | Dockerfile used to build your application image. |
| ``Pipfile`` | Python requirements installed via [pipenv](https://pipenv.pypa.io) |
| ``Pipfile.lock`` | Locked requirements (generated on first install). |
| ``app_data`` | Application data such as vocabularies. |
| ``assets`` | Web assets (CSS, JavaScript, LESS, JSX templates) used in the Webpack build. |
| ``docker`` | Example configuration for NGINX and uWSGI. |
| ``docker-compose.full.yml`` | Example of a full infrastructure stack. |
| ``docker-compose.yml`` | Backend services needed for local development. |
| ``docker-services.yml`` | Common services for the Docker Compose files. |
| ``invenio.cfg`` | The Invenio application configuration. |
| ``logs`` | Log files. |
| ``notes`` | CCA's documentation on running & developing the app |
| ``static`` | Static files that need to be served as-is (e.g. images). |
| ``templates`` | Folder for your Jinja templates. |
| ``.invenio`` | Common file used by Invenio-CLI to be version controlled. |
| ``.invenio.private`` | Private file used by Invenio-CLI *not* to be version controlled. |

## Documentation

To learn how to configure, customize, deploy and much more, visit the [InvenioRDM Documentation](https://inveniordm.docs.cern.ch/).
