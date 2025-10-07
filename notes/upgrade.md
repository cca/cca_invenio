# Upgrading Invenio

High-level Invenio upgrade:

- update services docker images (if needed)
- update Python packages
- upgrade database
- run upgrade script (e.g. "upgrade_scripts/migrate_10_0_to_11_0.py")
- rebuild static assets, see `invenio-cli assets` and `invenio webpack` (not included below)

The v10 and v11 upgrades below were performed with the "containerized" setup so they're not representative of an upgrade using the local/services setup.

## v13 Upgrade on Staging

- Build new "latest" staging image using v13 code (tag this repo `stg-build-X`)
- Restart all deployments to pull new images: `kubectl -ninvenio-dev rollout restart deploy -l app.kubernetes.io/name=cca-invenio`
- Run upgrade steps on an app pod:

```sh
# locally execute shell on an app pod, doesn't have to be "web" pod
POD=$(kubectl -ninvenio-dev get pods -o name -l app.kubernetes.io/component=web)
kubectl -ninvenio-dev exec ${POD} -it -- /bin/bash
# these commands are run on the pod
invenio alembic upgrade
invenio shell "$(find "${VIRTUAL_ENV}"/lib/*/site-packages/invenio_app_rdm -name migrate_12_0_to_13_0.py)"
invenio index destroy --yes-i-know # this cmd does not destroy the stats indices
# weren't these already deleted by `invenio index destroy`?
invenio index delete --force --yes-i-know "invenio-rdmrecords-records-record-*-percolators"
invenio index init
# if you have records custom fields
invenio rdm-records custom-fields init
# if you have communities custom fields
invenio communities custom-fields init
invenio rdm rebuild-all-indices
```

### `invenio-job` Problems

The `invenio-jobs` module was added with v13 but does not exactly work out of the box.

On our helm-managed staging instance, there is no new pod for [the job scheduler](https://inveniordm.docs.cern.ch/operate/customize/jobs/#scheduler). To fix this, we copied the worker-beat deployment template to make a worker-scheduler template.

The index setup commands did not create the job logs index. If yweou view a job run under Admin > Jobs `administration/runs/<uuid>`, we see an error due to the missing index. Niether `invenio index create invenio-job-logs` nor running an Invenio shell and using the`opensearchpy` client to create the index works, because it's a template index that creates data streams only. In the end, using the client to create a data stream eliminates the errors but log entries are still empty ([discord](https://discord.com/channels/692989811736182844/704625518552547329/1425201129104478208)):

```python
from flask import current_app
from opensearchpy import OpenSearch
os_client = OpenSearch(current_app.config['SEARCH_HOSTS'])
os_client.indices.create_data_stream(name='invenio-job-logs')
```

<details>
<summary>Errors</summary>

Error in web server logs when viewing a run: `opensearchpy.exceptions.NotFoundError: NotFoundError(404, 'index_not_found_exception', 'no such index [invenio-job-logs]', invenio-job-logs, index_or_alias).`![alt]( '{"class": "", "title": ""}')`

```python
# invenio shell trying to create index
client.indices.create('invenio-job-logs');
RequestError: RequestError(400, 'illegal_argument_exception', '''cannot create index with name [invenio-job-logs],
because it matches with template [invenio-job-logs-v1.0.0] that creates data streams only, use create data stream
api instead''')
```

</details>

### Image `KeyError`

For a long time (hours) after the upgrade, requests to the records API continued to fail with a `KeyError` that seemed to relate to statistics aggregation. This was despite the stats queues existing. I also ran `invenio stats events process` and `invenio stats aggregations process`. Perhaps things weren't fixed until those tasks completed in the background? It took a surprisingly long time, though.

<details>
<summary>Full stacktrace of "image" KeyError</summary>

```log
[2025-09-16 11:52:57,691] ERROR in app: Exception on /records [GET]
Traceback (most recent call last):
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask/app.py", line 1511, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask/app.py", line 919, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask/app.py", line 917, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask/app.py", line 902, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask_resources/resources.py", line 65, in view
    return view_meth()
           ^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask_resources/content_negotiation.py", line 116, in inner_content_negotiation
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask_resources/parsers/decorators.py", line 51, in inner
    return f(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask_resources/parsers/decorators.py", line 51, in inner
    return f(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/flask_resources/responses.py", line 39, in inner
    res = f(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/invenio_records_resources/resources/records/resource.py", line 86, in search
    return hits.to_dict(), 200
           ^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/invenio_records_resources/services/records/results.py", line 252, in to_dict
    if self.aggregations:
       ^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/invenio_records_resources/services/records/results.py", line 194, in aggregations
    return self._results.labelled_facets.to_dict()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/invenio_records_resources/services/records/facets/response.py", line 81, in labelled_facets
    self._labelled_facets[name] = facet.get_labelled_values(
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/invenio/.venv/lib/python3.12/site-packages/invenio_records_resources/services/records/facets/facets.py", line 227, in get_labelled_values
    "label": label_map[key],
             ~~~~~~~~~^^^^^
KeyError: 'image'
```

</details>

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
