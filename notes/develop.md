# Developing Invenio

## Getting started

### Language Versions

There is a ".tool-versions" file in the root of the project for the Python and Node versions which asdf or mise can use to set up those interpreters.

### Invenio Installation

See [Installation docs](https://inveniordm.docs.cern.ch/install/). We recommend the "local" or "services" setup which runs the main Invenio Flask application on our host machine using the code in this repository, while the database, search engine, task queue, and Redis cache are run as Docker containers. These steps only need to be run once. The [demo site's wipe_recreate.sh](https://github.com/inveniosoftware/demo-inveniordm/blob/master/demo-inveniordm/wipe_recreate.sh) script is a good reference for the exact steps needed to setup a fresh instance.

```sh
# to build fresh, answering configuration questions
invenio-cli init rdm -c 12.0
invenio-cli install all --dev
invenio-cli services setup --no-demo-data
```

To start the app, ensure Docker is running, spin up the services, and `run` the app.

```sh
docker desktop start
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
    "InvenioAppRdm.Deposit.AccordionFieldFunding.container": () => null,
}
```

Overriding an `AccordionField` like above removes an entire collapsible section from the deposit form, while we can also remove specific components from within a section (e.g. `InvenioAppRdm.Deposit.LanguagesField.container` removes only the **Languages** field from the **Recommended information** section).

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

### Editing/testing JS/CSS

`invenio-cli assets build` completely rebuilds the JS and CSS assets, installing remote packages and compiling the JS and CSS from scratch, overwriting local changes. Use `invenio-cli assets watch` to rebuild assets whenever the source files change, e.g. if editing an Invenio or site package. The packages are under the instance path in the assets directory and already compiled to ESM and commonjs formats. `invenio webpack build` rebuilds the assets.

`assets watch` is quicker than `assets build` but the UI still doesn't reflect changes, at least for custom fields component changes, we need to rerun it on each edit. `watch` runs with `NODE_ENV=development` so assets are not minified/obfuscated. This makes it far easier to use [React Developer Tools](https://chromewebstore.google.com/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi) and other debugging tools.

## Custom code & views

https://inveniordm.docs.cern.ch/develop/howtos/custom_code/

There is a demo of a custom view at `/vocablist` which lists all vocabs and links to their API routes.

## SAML Authentication

We want to eventually use [invenio-saml](https://invenio-saml.readthedocs.io/en/latest/) for SSO authentication. The [SAML integration](https://inveniordm.docs.cern.ch/customize/authentication/#saml-integration) section of the Invenio docs seems to have the most specific setup instructions.

## Testing Invenio core modules

See, for instance, [invenio-rdm-records](https://github.com/inveniosoftware/invenio-rdm-records) where it says how to install dependencies and run tests. These steps aren't enough, however, they don't include some necessary modules.

```sh
pipenv --python 3.12
pipenv shell
pip install -e .[all]
pip install invenio-search[opensearch2] invenio-db[postgresql] docker-services-cli check_manifest sphinx
```

To run tests, ensure Docker is running and `./run-tests.sh`.
