# Upgrading Invenio

High-level Invenio upgrade:

- update services docker images
- update Python packages
- upgrade database
- run upgrade script (e.g. "upgrade_scripts/migrate_10_0_to_11_0.py")
- rebuild static assets? see `invenio-cli assets` and `invenio webpack` (not included below but must be necessary)

The v10 and v11 upgrades below were performed with the "containerized" setup so they're not fully representative of an upgrade using the local/services setup. **TODO** practice an upgrade (11 -> 12?) with services setup

## 11.0.0 upgrade

First, read the release notes for upgrade considerations: https://inveniordm.docs.cern.ch/releases/upgrading/upgrade-v11.0/

Stop containers
Edit Dockerfile to reference the new CERN base image
Update invenio-cli in the venv
Edit Pipfile to set invenio version to 11
`invenio-cli packages update 11.0.0`
`invenio-cli containers build`
`invenio-cli containers start`
then, inside the web-ui container, `invenio alembic upgrade`
the "data migration" step is another one that doesn't make sense if you're using containers, it asks you to run `pipenv` commands but the way the containers are `pipenv` is using the system site packages and not a venv. So I used `python -m site` to find my python's site packages and then found the script being referred to and ran
`invenio shell /usr/local/lib/python3.9/site-packages/invenio_app_rdm/upgrade_scripts/migrate_10_0_to_11_0.py`

```sh
vim Pipfile # update invenio-cli and invenio versions
pipenv install
invenio-cli packages update 11.0.0
invenio-cli containers build
invenio-cli containers start
docker exec -it invenio-web-ui-1 /bin/bash
invenio alembic upgrade
invenio shell /usr/local/lib/python3.9/site-packages/invenio_app_rdm/upgrade_scripts/migrate_10_0_to_11_0.py
```

## 10.0.0 upgrade

Edited Pipfile to reference Invenio 10.0.0

`invenio-cli containers build` failed with errors related to webpack and missing assets from the new custom fields feature

Had to edit .invenio, add `search = elasticsearch7` line

on web-ui container

```sh
cd /opt/invenio/src
vim .invenio # add "search = elasticsearch7" line under [cookiecutter]
pipenv install invenio-cli==1.0.6
invenio-cli packages update 10.0.0
invenio-cli assets build
```

none of the invenio or invenio-cli commands work on the container because they expect pipenv to have made a virtualenv but the Dockerfile installs the dependencies into the system python environment

exit and `invenio-cli containers build` on the host
