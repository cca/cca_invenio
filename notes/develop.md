# Developing Invenio

## Getting started

### Language Versions

There is a ".tool-versions" file in the root of the project for the Python and Node versions which asdf or mise can use to set up those interpreters. Invenio supports Python 3.9 at the latest (as of 03/2023) and only Node 16. Python 3.12 and Node 20 support are on the way.

### Invenio Installation

See [Installation docs](https://inveniordm.docs.cern.ch/install/). We recommend the "local" or "services" setup which runs the main Invenio Flask application on our host machine using the code in this repository, while the database, search engine, task queue, and Redis cache are run as Docker containers. These steps only need to be run once. The [demo site's wipe_recreate.sh](https://github.com/inveniosoftware/demo-inveniordm/blob/master/demo-inveniordm/wipe_recreate.sh) script is a good reference for the exact steps needed to setup a fresh instance.

```sh
# to build fresh, answering configuration questions
invenio-cli init rdm -c 11.0
invenio-cli install --dev
invenio-cli services setup --no-demo-data
```

To start the app, ensure Docker is running, spin up the services, and `run` the app.

```sh
invenio-cli services start
invenio-cli run
```

If rebuilding a local instance, use `invenio-cli install --dev` to recreate the virtualenv. A mere `pipenv install` won't copy over the configuration and static files to a location inside the venv and the app breaks.

Invenio initializes fixtures (basically, the static app_data files) asynchronously by sending them to its task queue. So the initial startup, even after services are running, is further delayed as these tasks finish. We can view the task queue in the RabbitMQ dashboard and the size of the search indices to get a sense of how much processing is left. See the **Services** table in [run.md](run.md). The **Setup Troubles**  section may also be useful.

Once running, visit https://127.0.0.1:5000 in a web browser. **Note**: The server is using a self-signed SSL certificate, so our browser issues a warning that we have to by-pass.

The super admin is archives@cca.edu with password "password", this comes from app_data/users.yaml. We may need to `invenio users activate archives@cca.edu` the admin account.

## Frontend: Theme & Templates

Lots of UI variables to override and we can specify an additional stylesheet.

Create a template in the same path as existing one e.g. /templates/semantic-ui/invenion_app_rdm/frontpage.html but how easy/important will it be to merge updates to the base template into the customized one?

### Remove fields from upload form

https://inveniordm.docs.cern.ch/develop/howtos/override_components/

- find the field's `Overridable` component on the deposit form https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm/deposit/RDMDepositForm.js
- copy the `id` attribute
- in assets/js/invenio_app_rdm/overridableRegistry/mapping.js add a line to the `overriddenComponents` hash:

```js
export const overriddenComponents = {
    "InvenioAppRdm.Deposit.FundingField.layout": () => null,
}
```

If all of the children of a section with an accordion header are removed, the accordion remains but is empty. Awkward. Waiting on [a PR](https://github.com/inveniosoftware/invenio-app-rdm/pull/2087) (merged, but not in v11, v12 maybe?) to make it so we can remove the parent AccordionField as well.

### Custom JavaScript

To add custom JS to a template, we need to override the template, add a webpack entrypoint, and reference the script in the template. At a high level:

- create the script in site/cca/assets/semanti-ui/js/cca
- add its entry to site/cca/webpack.py like `'test': './js/cca/test.js'`
- use the alias we defined above when inserting it into a template

```html
<!-- add to existing js block or create new one like this: -->
{% block javascript %}
    {{ super() }}
    {{ webpack['test.js'] }}
{% endblock %}
```

Then rebuild the JS assets & restart the app: `invenio-cli assets build && invenio-cli run`

### Editing/testing core JS/CSS

`invenio-cli assets build` completely rebuilds the JS and CSS assets, installing remote packages and compiling the JS and CSS from scratch, overwriting local changes. Use `invenio-cli assets watch` to rebuild assets whenever the source files change, e.g. if editing an Invenio or site package. The packages are under the instance path in the assets directory and already compiled to ESM and commonjs formats. There's a Pipfile script `pipenv run instancepath` which echoes the path to the instance directory, so `cd (pipenv run instancepath)/assets` takes us there and `invenio webpack build` rebuilds the assets.

## Custom code & views

https://inveniordm.docs.cern.ch/develop/howtos/custom_code/

There is a demo of a custom view at `/vocablist` which lists all vocabs and links to their API routes.

## Testing Invenio core modules

See, for instance, [invenio-rdm-records](https://github.com/inveniosoftware/invenio-rdm-records) where it says how to install dependencies and run tests. These steps aren't enough, however, they don't include two necessary modules.

```sh
pipenv --python 3.9
pipenv shell
pip install -e .[all]
pip install invenio-search[opensearch2] invenio-db[postgresql] docker-services-cli check_manifest sphinx
```

Then to run tests, ensure Docker is running and `./run-tests.sh`.

## GitHub _and_ GitLab?!?

I want the project features of GitHub as well as the ability to easily write Markdown links to the various Invenio software projects, but we use GitLab for our CI/CD. I originally tried mirroring the GH repo in GL, but that proved too slow. Instead, we can use a remote with multiple push URLs:

```sh
git remote set-url --push --add origin git@github.com:cca/cca_invenio.git
git remote set-url --push --add origin git@gitlab.com:california-college-of-the-arts/invenio.git
```

Then `git push` updates both remotes at once. The `origin` remote's fetch URL can theoretically be either URL.
