# Configuration

https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/config.py

See invenio.cfg which has numerous comments.

## General Notes

When an invenio.cfg setting changes, the dev server reloads with the new value. But some settings are pseudo-fixtures that are used only during initialization (the RDM passwords field, custom fields?).

If a fixture in app_data changes, then the whole app needs to be rebuilt. See `./notes/code-samples/rebuild`. This deletes the database and search indices.

## [Vocabularies](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/#vocabularies)

Much of the work creating these is in the [migration repo](https://github.com/cca/vault_migration).

- Subjects
  - Custom local/CCA subjects for terms not found in LC (e.g. specific CCA properties)
  - ~~AAT subjects~~ not enough to justify
  - LC vocabs (LCSH, LCNAF, LCGFT) terms we've used before
  - Temporal (list of decades)
- Names (autofill in "Creatributors" modal, from integrations JSON)
- Users (actual accounts, from integrations JSON)

Should we combine several vocabs as one "CCA" subject? **Pros**: one single entry in subjects drop-down. **Cons**: odd mixture of terms serving different purposes.

### Updating Vocabularies

For [Names](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/names/#how-to-import-and-update-your-name-records), new ones can be updated with `invenio vocabularies update -v names -f ./app_data/vocabularies_future.yaml` where that yaml config references the names to be loaded in app_data/vocabularies/names.yaml. Note the relative path; that is relative to where you run the `invenio` command, not relative to the vocabularies_future.yaml file.

```yaml
names:
  readers:
    - type: yaml
      args:
        origin: "./app_data/vocabularies/names.yaml"
  writers:
    - type: names-service
      args:
        update: true
```

There is also an `invenio rdm-records add-to-fixture` command as of v12. This uses the vocabularies.yaml file but I'm not sure which vocabularies it's capable of updating.

## Secret Manager

We store environment-dependent configuration values in [Google Secret Manager](https://console.cloud.google.com/security/secret-manager?project=cca-web-staging). Each instance, including a dev environment running on localhost, has its own JSON secrets. We need at least an `ENVIRONMENT` env var to determine if we are running `local`, `staging`, or `production`. The `staging` and `production` instances also need a `GSM_CREDENTIALS` env var for a service account that can authenticate to their secret. Locally, we can set `ENVIRONMENT=local` and `CCA_SECRETS=secret.json` to use a local JSON file instead of GSM. It is recommended to test with a secret.json file only temporarily and to delete it once finished.

While the main app loads values in a .env file, the celery background workers do not. We must export `ENVIRONMENT`, `CCA_SECRETS`, `AWS_REQUEST_CHECKSUM_CALCULATION`, and `AWS_RESPONSE_CHECKSUM_VALIDATION` to run the app locally. `mise` does this automatically.

To see the necessary values, view an existing secret. They are not necessarily confidential information, but values that change per instance, like hostnames. Here's an example (some fields may be missing):

```json
{ "APP_ALLOWED_HOSTS": ["127.0.0.1"],
"INVENIO_SECRETKEY": "changeme",
"INVENIO_SQLALCHEMY_DATABASE_URI": "postgresql+psycopg2://invenio:invenio@localhost/invenio",
"POSTGRES_PASSWORD": "invenio",
"POSTGRES_USERNAME": "invenio",
"RABBITMQ_PASSWORD": "password",
"S3_ENDPOINT_URL": "https://storage.googleapis.com/invenio-local",
"S3_REGION_NAME": "us-west1",
"S3_ACCESS_KEY_ID": "service account hmac key",
"S3_SECRET_ACCESS_KEY": "service account hmac secret",
"SITE_UI_URL": "https://127.0.0.1:5000",
"SITE_API_URL": "https://127.0.0.1:5000/api" }
```

For remote (staging, prod) instances, we also need to create a Service Account which will authenticate with Secret Manager:

```bash
# create the service account in the appropriate project
gcloud iam service-accounts create invenio-staging-secrets --display-name "Invenio Staging Secrets" --project cca-web-staging
# allow the service account to access Secret Manager
gcloud secrets add-iam-policy-binding invenio_staging --member="serviceAccount:invenio-staging-secrets@cca-web-staging.iam.gserviceaccount.com" --project="cca-web-staging" --role="roles/secretmanager.secretAccessor"
# create a JSON key for the service account
gcloud iam service-accounts keys create key.json --iam-account invenio-staging-secrets@cca-web-staging.iam.gserviceaccount.com
```

Finally, when installing our helm chart we set a `GSM_CREDENTIALS` environment variable with the contents of the key like `helm install ... --set invenio.extraConfig.GSM_CREDENTIALS="(cat key.json)"` (or `$(cat key.json)` for bash shell).

## Security, Users

Users are created by app_data/[users.yaml](https://inveniordm.docs.cern.ch/operate/customize/users/). We create a default "archives@cca.edu" superadmin with password "password". Passwords can also be defined in invenio.cfg by `RDM_RECORDS_USER_FIXTURE_PASSWORDS`. Passwords in the setting override passwords in users.yaml.

We set `ACCOUNTS_LOCAL_LOGIN_ENABLED = True` during local dev but it's `False` when we're using SSO.

As of v11, there is a `--confirm` flag so you can `invenio users create -c` to automatically confirm the created user.

To give an account admin permissions, run: `uv run invenio roles add <email> admin`

See the [SAML Integration](https://inveniordm.docs.cern.ch/operate/customize/authentication/#saml-integration) documentation.

## Translations

To change the text in the user interface, we create a translation which maps the default to our text. Edit the [messages.po](../translations/en/LC_MESSAGES/messages.po) file:

```pot
#: invenio_app_rdm/records_ui/templates/semantic-ui/invenio_app_rdm/records/detail.html:223
msgid "Published"
msgstr "Created"
```

The `msgid` is the original string while `msgstr` is our translation. The `#` comment above helps identify where the text is used in code. Then we use the `invenio-cli` [translations](https://inveniordm.docs.cern.ch/reference/cli/#translations-commands) command `invenio-cli translations compile` to compile binary message catalogs and symlink them into the app instance.

Not sure what a string is? Most are referenced in [the invenio-app-rdm translations](https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/translations/messages.pot), but we can also `invenio-cli translations extract` to find translated strings in Invenio code. We can verify a compiled messages.mo file has the text we want with the `msgunfmt` utility by running `msgunfmt translations/en/LC_MESSAGES/messages.mo`.

## Storage

Invenio works with Amazon S3. We use a Google Storage Bucket with some interoperability considerations.

- Use appropriate Google Cloud project (e.g. staging versus prod)
- Under Cloud Storage > Buckets, create a private storage bucket. Invenio handles authorization.
  - Single location like `us-west1` for staging, consider multi-region for production
  - Select **Autoclass** when creating the bucket and opt-in to Coldline/Archive classes
  - **Prevent public access** and use **Uniform** access control
  - We should consider soft delete and object versioning for production to reduce chances of accidental data loss
  - Allow CORS from the Invenio domain, `gcloud storage buckets update gs://invenio-local --cors-file notes/cors.json` where [cors.json](./cors.json) lists the instance domain(s), or else PDF previews won't work
- Under IAM > Service Accounts, create a service account with no project-level permissions nor user access `gcloud iam service-accounts create invenio-local-gsb --display-name "Invenio Local Files" --project cca-web-staging`
- Go to the bucket > **Permissions** > **Grant Access** and give the service account the **Storage Object Admin** role `gsutil iam ch serviceAccount:invenio-local-gsb@cca-web-staging.iam.gserviceaccount.com:objectAdmin gs://invenio-local`
- Create a [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) for the service account, save the key and secret to Dashlane (**this is the only time the secret is shown**) `gsutil hmac create invenio-local-gsb@cca-web-staging.iam.gserviceaccount.com`
- Add necessary `S3_...` variables to [Secret Manager](#secret-manager) and to invenio.cfg (see below)
- Add `AWS_REQUEST_CHECKSUM_CALCULATION="WHEN_REQUIRED"` & `AWS_RESPONSE_CHECKSUM_VALIDATION="WHEN_REQUIRED"` env vars (e.g. to a .env file locally or an extraEnvVars property in the helm chart)

```python
# Invenio-Files-Rest
# ==================
FILES_REST_STORAGE_FACTORY = "invenio_s3.s3fs_storage_factory"

# Invenio-S3
# https://invenio-s3.readthedocs.io/en/latest/configuration.html
# In actual invenio.cfg these will be secrets["VAR_NAME"] values instead
S3_ENDPOINT_URL = "https://storage.googleapis.com"
S3_REGION_NAME = "us-west1"
S3_ACCESS_KEY_ID = "HMAC key"
S3_SECRET_ACCESS_KEY = "HMAC secret"

# Allow S3 endpoint in the CSP rules
APP_DEFAULT_SECURE_HEADERS["content_security_policy"]["default-src"].append(
    S3_ENDPOINT_URL
)
```

Finally, Invenio might not initialize the correct files location by default. We can run `invenio files location create gs-invenio-local s3://invenio-local --default` to create a new default location pointing to the storage bucket.

The .invenio file also has `file_storage = S3` but that file might only be used when invenio-cli bootstraps a new instance. When we choose S3 storage during `invenio-cli init`, we get a [Minio](https://github.com/minio/minio) service too, but it is not necessary to use it to use cloud storage.

## Custom Fields

- Simplest: https://inveniordm.docs.cern.ch/operate/customize/metadata/custom_fields/records/
- Reference: https://inveniordm.docs.cern.ch/operate/customize/metadata/custom_fields/widgets/
- Build your own: https://inveniordm.docs.cern.ch/operate/customize/metadata/custom_fields/custom_fields/

Managed to build a custom "Academic Programs" field that uses a vocabulary, autocompletes on the form, and has a custom display template linking to search results sharing the same value (similar to how we do it in VAULT). The only thing that did not work is that the search facet does not appear, but the indexing clearly works because the hyperlinked search returns results. One other disappointment is that, though I defined a bunch of properties for each term in the related programs vocab, it only records the `id` and `title` in the record.

Our `ArchivesSeriesCF` is a custom field with our own structure (dictionary) and deposit form widget. We can build custom fields that do almost anything with this approach, which is not limited to the few types of custom fields Invenio provides. The biggest challenge is writing the React form widget. Helpful reference points are [Semantic UI React](https://react.semantic-ui.com/) and [react-invenio-forms](https://github.com/inveniosoftware/react-invenio-forms), specifically the [forms components](https://github.com/inveniosoftware/react-invenio-forms/tree/master/src/lib/forms). Sometimes limitations in one component force us to use a lower level one. Read the source code of components to understand how they work and what props they accept. For instance, `Dropdown` does not support change handlers, but it is a wrapper around `SelectField` which does.

[Formik](https://formik.org/docs/overview) is used for form state management and validation. You can `useFormikContext` in a functional React component to access the deposit form's current values, which allows you to make conditional fields.

We have two demo custom fields `ConditionalField` and `CommunityField` which demonstrate conditional inputs that only show on the deposit form some of the time. `ConditionalField` checks if another metadata field has a particular value and disables the field if the condition is not met. `CommunityField` is analogous and shows only for submissions to a specific community.

The `props` passed to a custom field React components represent only the initial state of the record (e.g. they only have data for drafts or new versions being edited). In order to access the current and mutable state of the form, we have to use Formik and Redux.
