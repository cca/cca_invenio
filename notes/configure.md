# Configuration

https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/config.py

See invenio.cfg which has numerous comments.

## General Notes

When a setting changes, such as something defined in invenio.cfg, you can simply reload the app (stop and then `invenio-cli run` again) to see the change. But some settings are like pseudo-fixtures that are using only during initialization (the RDM passwords field, custom fields?).

If a fixture in app_data changes, then the whole app needs to be rebuilt. Run `./notes/code-samples/rebuild`. This deletes the database and search indices.

## [Vocabularies](https://inveniordm.docs.cern.ch/customize/vocabularies/)

- ~~AAT subjects~~ not enough to justify
- Custom local/CCA subjects for terms not found in LC (e.g. specific CCA properties)
- LC vocabs (LCSH, LCNAF, LCGFT) terms we've used before
- Temporal (list of decades)
- Names (from Libraries subject names taxo)
- Users (from our integrations JSON)

Should we combine several vocabs as one "CCA" subject? **Pros**: one single entry in subjects drop-down. **Cons**: odd mixture of terms serving different purposes.

For [Names](https://inveniordm.docs.cern.ch/customize/vocabularies/names/), new ones can be added with `invenio vocabularies -v names -f ./app_data/vocabularies-future.yaml` where that yaml config references the names to be loaded in app_data/names.yaml. I haven't figured out how to load names without a real identifier (like ORCID).

## Security, Users

Users are created by app_data/[users.yaml](https://inveniordm.docs.cern.ch/customize/vocabularies/users/). We create a default "archives@cca.edu" superadmin with password "password". Passwords can also be defined in invenio.cfg by `RDM_RECORDS_USER_FIXTURE_PASSWORDS`. Passwords in the setting override passwords in users.yaml.

There are many invenio.cfg boolean settings we'll need to flip when we switch to SSO.

- `USERPROFILES_READ_ONLY = False` set to `True` to prevent users from editing their emails?
- `ACCOUNTS_LOCAL_LOGIN_ENABLED = True` allow local accounts (versus OAuth or SSO accounts)
- `SECURITY_REGISTERABLE = True` allows users to register
- `SECURITY_RECOVERABLE = True`  allows users to reset the password
- `SECURITY_CHANGEABLE = True`  allows users to change their password

These two settings let users to sign up and login without confirming their email, which is useful during development.

- `SECURITY_CONFIRMABLE = False`  # local login: users can confirm e-mail address
- `SECURITY_LOGIN_WITHOUT_CONFIRMATION = True` # require users to confirm email before being able to login

As of v11, there is a `--confirm` flag so you can `invenio users create -c` to automatically confirm the created user.

To give an account admin permissions, run: `pipenv run invenio roles add <email> admin`

See the [SAML Integration](https://inveniordm.docs.cern.ch/customize/authentication/#saml-integration) documentation.

## Storage

Invenio works with Amazon S3. We use a Google Storage Bucket with some interoperability considerations.

- Use appropriate Google Cloud project (e.g. staging versus prod)
- Under Cloud Storage > Buckets, create a storage bucket with Standard storage class and no public access. Invenio runs requests for files through the application, so we can have private items.
  - @TODO should we use Autoclass instead of Standard? Is it worth it? Pending research.
  - @TODO Object protection measures. If we use, for instance, object versioning do we need fewer backups?
- Under IAM > Service Accounts, create a service account with no project-level permissions and no user access, then go to the bucket you created > Permissions > Grant Access and enter the service account, give it Storage Object Admin role
- Create a [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) for the service account, save the key and secret to Dashlane (**this is the only time the secret is shown**)
- Add S3 storage configuration to invenio.cfg (see below)

```ini
# Invenio-Files-Rest
# ==================
FILES_REST_STORAGE_FACTORY='invenio_s3.s3fs_storage_factory'

# Invenio-S3
# ==========
S3_ENDPOINT_URL=f'https://storage.googleapis.com/BUCKET_NAME'
S3_ACCESS_KEY_ID='HMAC key'
S3_SECRET_ACCESS_KEY='HMAC secret'

# Allow S3 endpoint in the CSP rules
APP_DEFAULT_SECURE_HEADERS['content_security_policy']['default-src'].append(
    S3_ENDPOINT_URL
)
```

The .invenio file also has `file_storage = S3` but that file might just be used when invenio-cli bootstraps a new instance.

@TODO When choose S3 storage during `invenio-cli init` you get a Minio service too, we need to [follow the steps](https://inveniordm.docs.cern.ch/customize/s3/#set-your-minio-credentials) to change the admin account credentials and hook it up to GSB.

## Custom Fields

Simplest: https://inveniordm.docs.cern.ch/customize/custom_fields/records/
Reference: https://inveniordm.docs.cern.ch/reference/widgets/#autocompletedropdown
Build your own: https://inveniordm.docs.cern.ch/develop/howtos/custom_fields/

Managed to build a custom "Academic Programs" field in around an hour that uses a vocabulary, autocompletes on the form, and has a custom display template linking to search results sharing the same value (similar to how we do it in VAULT). The only thing that did not work is that the search facet does not appear, but the indexing clearly works because the hyperlinked search returns results.

One other disappointment is that, though I defined a bunch of properties in for each term in the related programs vocab, it only records the `id` and `title` in the record.
