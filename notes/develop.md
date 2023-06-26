# Developing Invenio

## Getting started

See [Installation docs](https://inveniordm.docs.cern.ch/install/). We recommend the "local" or "services" setup which runs the main Invenio Flask application on your host machine using the code in this repository, while the database, search engine, task queue, and redis cache are run as Docker containers. These steps only need to be run once.

```sh
# to build fresh, answering configuration questions
invenio-cli init rdm -c 11.0
invenio-cli install
```

To start the app, ensure Docker is running, spin up the services, and `run` the app.

```sh
invenio-cli services setup
invenio-cli run
```

The build process is slow the first time as docker images have to be downloaded during the process.

Invenio initializes fixtures (basically, the static app_data files) asynchronously by sending them to its task queue. So the initial startup, even after services are running, is further delayed as these tasks finish.

See also: **Setup Troubles** in [run.md](run.md) if the app doesn't work at first.

Once running, visit https://127.0.0.1:5000 in a web browser. **Note**: The server is using a self-signed SSL certificate, so your browser will issue a warning that you will have to by-pass.

The super admin is admin@inveniosoftware.org with password `password`, based on `RDM_RECORDS_USER_FIXTURE_PASSWORDS` in invenio.cfg. If not, [reset the password](https://inveniordm.docs.cern.ch/customize/vocabularies/users/#change-password).

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