# Developing Invenio

## Getting started

### Languages and Tools

There is an [asdf](https://asdf-vm.com/) ".tool-versions" file in the root of the project. Invenio supports Python 3.9 at the latest (as of 03/2023) and only Node 16. Follow the asdf setup instructions and add the python and nodejs plugins, then install the appropriate versions. Note that asdf can conflict with other version managers like pyenv and nvm, so you may need to uninstall those or make sure asdf takes priority in your `PATH`.

```sh
brew install asdf
# add asdf to your shell profile
# see https://asdf-vm.com/guide/getting-started.html
asdf plugin add python
asdf plugin add nodejs
asdf install
```

Installing `invenio-saml` requires an outdated version of `xmlsec1` (see [#17](https://github.com/cca/cca_invenio/issues/17))which isn't in Homebrew. Eric made a local tap for the requisite version. First, download install Xcode and open it to accept the license agreement. Then `brew tap phette23/local` and `brew install xmlsec1@1.2.37`.

### Invenio Installation

See [Installation docs](https://inveniordm.docs.cern.ch/install/). We recommend the "local" or "services" setup which runs the main Invenio Flask application on your host machine using the code in this repository, while the database, search engine, task queue, and redis cache are run as Docker containers. These steps only need to be run once.

```sh
# to build fresh, answering configuration questions
invenio-cli init rdm -c 11.0
invenio-cli install
invenio-cli services setup
```

To start the app, ensure Docker is running, spin up the services, and `run` the app.

```sh
invenio-cli services start
invenio-cli run
```

If rebuilding a local instance, use `invenio-cli install -d` to recreate the virtualenv. A mere `pipenv install` won't copy over the configuration and static files to a location inside the venv and the app breaks.

The build process is slow the first time as docker images are downloaded.

Invenio initializes fixtures (basically, the static app_data files) asynchronously by sending them to its task queue. So the initial startup, even after services are running, is further delayed as these tasks finish. View the task queue in the RabbitMQ dashboard and the size of the search indices to get a sense of how much processing is left. See the **Services** table in [run.md](run.md). The **Setup Troubles**  section may also be useful.

Once running, visit https://127.0.0.1:5000 in a web browser. **Note**: The server is using a self-signed SSL certificate, so your browser will issue a warning that you have to by-pass.

The super admin is archive@cca.edu with password "password", this comes from app_data/users.yaml. You may need to `invenio users activate archive@cca.edu` the admin account.

## Theme & Templates

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

If all of the children of a section with an accordion header are removed, the accordion remains but is empty. Awkward.Waiting on [a PR](https://github.com/inveniosoftware/invenio-app-rdm/pull/2087) (merged, but not in v11) to make it so we can remove the parent AccordionField as well.

## Custom code & views

https://inveniordm.docs.cern.ch/develop/howtos/custom_code/

There is a custom view at `/vocablist` which lists all vocabs and links to their API routes.

### Custom JavaScript

To add custom JS to a template, you'll need to override the template, add a webpack entrypoint, and reference the script in the template. At a high level:

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

## Testing Invenio core modules

See, for instance, [invenio-rdm-records](https://github.com/inveniosoftware/invenio-rdm-records) where it says how to install dependencies and run tests. These steps won't be enough, however, they don't include two necessary modules. It's also not clear to me why we're installing things one-by-one, doing as much typing as possible.

```sh
pipenv --python 3.9
pipenv shell
pip install -e .[all]
pip install invenio-search[opensearch2] invenio-db[postgresql] docker-services-cli check_manifest sphinx
```

Then to run tests, ensure Docker is running, and `./run-tests.sh`.

## GitHub _and_ GitLab?!?

I want the project features of GitHub as well as the ability to easily write Markdown links to the various Invenio software projects, but we use GitLab for our CI/CD. I originally tried mirroring the GH repo in GL, but that proved too slow. Instead, we can use a remote with multiple push URLs:

```sh
git remote set-url --push --add origin git@github.com:cca/cca_invenio.git
git remote set-url --push --add origin git@gitlab.com:california-college-of-the-arts/invenio.git
```

Then `git push` updates both remotes at once. The `origin` remote's fetch URL can theoretically be either URL.
