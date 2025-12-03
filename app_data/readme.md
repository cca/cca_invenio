# README

This directory contains static fixtures that are ingested when the app is initialized. _Updating the data here does not update the corresponding data in the app_. For that, use `invenio rdm-records add-to-fixture` or `invenio vocabularies update`.

The **pages** folder is for [static pages](https://inveniordm.docs.cern.ch/operate/customize/static_pages/).

The **vocabularies** folder is for the various types of [vocabularies](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/#vocabularies). These cover more functions than you might expect, including resource types and subjects. There are different types of vocabs and they may be structured differently. We can also create custom vocabs which are used by custom fields, but they must use an existing vocabulary type (usually subject?).

Many default vocabularies are in the [invenio-rdm-records](https://github.com/inveniosoftware/invenio-rdm-records) repository under the fixtures > data > [vocabularies](https://github.com/inveniosoftware/invenio-rdm-records/tree/master/invenio_rdm_records/fixtures/data/vocabularies) directory.

## Subjects

To see what is in a particular subject scheme: `https://127.0.0.1:5000/api/subjects?q=scheme:form`.

Each subject is a separate vocabulary, but does not have its own API route, they're unified under `/api/subjects`.

To add to a subject: `uv run invenio rdm-records add-to-fixture form`. This appears to run over all entires in [vocabularies.yaml](vocabularies.yaml) even if only one is specified, adding missing terms.

If we change the label of a subject with the REST API, existing records show the updated label because Invenio stores an ID reference and not the text of the label.

Subject term IDs cannot be shared across schemes.

**Do not delete terms**. If we delete a term, records throw `AttributeError: 'NoneType' object has no attribute 'id'`! To fix this, we either have to edit the record to remove references _beforehand_ (unsure if we can do it after) or permanently delete the PID in the database (using `psql`, unsure if `invenio_pidstore` code can delete).

### REST API Modifications

While it's not advertised in [the Vocabularies REST API docs](https://inveniordm.docs.cern.ch/reference/rest_api_vocabularies/) the full suite of CRUD operations work;`POST`, `PUT`, and `DELETE`.

```python
import os
from requests import Session

token = os.getenv("TOKEN") or os.getenv("INVENIO_TOKEN", "")
http = Session()
http.headers.update({"Authorization": f"Bearer {token}"})
http.headers.update({"Content-Type": "application/json"})
http.verify = False
subject = {
    "id": "ef4a04c3-05ca-5ec6-abf5-2fd0dae0a8f8",
    "scheme": "place",
    "title": {"en": "Martinez Hall Mural Wall"},
}
r = http.post("https://127.0.0.1:5000/api/subjects", json=subject) # create
print(r.status_code)
subject["scheme"] = "topic" # change the scheme of a subject
r = http.put(f"https://127.0.0.1:5000/api/subjects/{subject['id']}", json=subject) # update
# ! WARNING! Deleted terms render their ID unusable.
r = http.delete(f"https://127.0.0.1:5000/api/subjects/{subject['id']}") # delete
print(r.status_code)
```

We may need to use `"title": {"en": "Title"}` when creating terms but `"subject": "Title"` when modifying. Subjects only have a subject when you `GET` them. Modifing their `title` works but it also causes the subject to look different, containing both a subject and title. Use only "subject" if possible.
