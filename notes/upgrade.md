# Upgrading Invenio

High-level Invenio upgrade:

- update services docker images (if needed)
- update Python packages
- upgrade database
- run upgrade script (e.g. "upgrade_scripts/migrate_10_0_to_11_0.py")
- rebuild static assets, see `invenio-cli assets` and `invenio webpack` (not included below)

The v10 and v11 upgrades below were performed with the "containerized" setup so they're not representative of an upgrade using the local/services setup.

## 13.0.2 upgrade

Change `APP_ALLOWED_HOSTS` to `TRUSTED_HOSTS` in [invenio.cfg](/invenio.cfg).

Add .mjs javascript type to nginx.conf for new PDF previewer.

```sh
# invenio-cli packages update 13.0.2
# maybe I should've done the recommended cmd above instead of `uv` because
# below I have to manually build the frontend assets
uv add invenio-app-rdm[opensearch2, s3]==13.0.2
uv sync
invenio-cli assets build -d
source .venv/bin/activate.fish
# with the app running or maybe at least the workers?
invenio alembic upgrade
invenio shell (find .venv/lib/*/site-packages/invenio_app_rdm -name migrate_12_0_to_13_0.py)
invenio index destroy --yes-i-know # this cmd does not destroy the stats indices
set search_prefix invenio
# weren't these already deleted by `invenio index destroy`?
invenio index delete --force --yes-i-know "$search_prefix-rdmrecords-records-record-*-percolators"
invenio index init
# if you have records custom fields
invenio rdm-records custom-fields init
# if you have communities custom fields
invenio communities custom-fields init
invenio rdm rebuild-all-indices
```

## 12.0.0 upgrade

https://inveniordm.docs.cern.ch/releases/upgrading/upgrade-v12.0/

Remove the existing virtualenv `pipenv --rm`.
Update to more current Python and Node versions. Edit Pipfile, .tool-versions, and `mise install` or `asdf install`.

```sh
invenio-cli packages update 12.0.0 # this updates Pipfile
pipenv uninstall flask-babelex # not needed if we rebuild the venv?
invenio-cli assets build # also not needed with below?
invenio-cli install --dev
```

Change `from flask_babelex import lazy_gettext as _` to `from invenio_i18n import lazy_gettext as _` in [invenio.cfg](../invenio.cfg).

At first, the alembic upgrade below failed with `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "invenio-app-rdm"` when our db user is "invenio" because I hadn't run `invenio-cli install` so it was not reading our invenio.cfg file.

```sh
invenio-cli packages lock
pipenv shell # must be in venv for `invenio` (no -cli) cmds
invenio alembic upgrade # db migration
invenio queues declare # add statistics processing queues
# "data migration"
invenio shell (find (pipenv --venv 2>/dev/null)/lib/*/site-packages/invenio_app_rdm -name migrate_11_0_to_12_0.py)
# rebuild search indices
invenio index destroy --yes-i-know
invenio index init
invenio rdm rebuild-all-indices
# new roles
invenio roles create administration-moderation
invenio roles create administration
invenio access allow administration-moderation role administration-moderation
invenio access allow administration-access role administration
invenio access allow superuser-access role administration
```

Somewhere along this process deleted the instance's data directory (`(pipenv --venv 2>/dev/null)/var/instance/data`).

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

Edited Pipfile to reference Invenio 10.0.0.

`invenio-cli containers build` failed with errors related to webpack and missing assets from the new custom fields feature.

Had to edit .invenio, add `search = elasticsearch7` line.

On web-ui container:

```sh
cd /opt/invenio/src
vim .invenio # add "search = elasticsearch7" line under [cookiecutter]
pipenv install invenio-cli==1.0.6
invenio-cli packages update 10.0.0
invenio-cli assets build
```

None of the invenio or invenio-cli commands work on the container because they expect pipenv to have made a virtualenv but the Dockerfile installs the dependencies into the system python environment.

Exit and `invenio-cli containers build` on the host.
