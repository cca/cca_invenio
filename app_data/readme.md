# README

This directory contains static fixtures that are ingested when the app is initialized. _Updating the data here does not update the corresponding data in the app_. For that, use `invenio rdm-records add-to-fixture` or `invenio vocabularies update`.

The **pages** folder is for [static pages](https://inveniordm.docs.cern.ch/operate/customize/static_pages/).

The **vocabularies** folder is for the various types of [vocabularies](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/#vocabularies). These cover more functions than you might expect, including resource types and subjects. There are different types of vocabs and they may be structured differently. We can also create custom vocabs which are used by custom fields, but they must use an existing vocabulary type (usually subject?).

Many default vocabularies are in the [invenio-rdm-records](https://github.com/inveniosoftware/invenio-rdm-records) repository under the fixtures > data > [vocabularies](https://github.com/inveniosoftware/invenio-rdm-records/tree/master/invenio_rdm_records/fixtures/data/vocabularies) directory.

## Subjects

To see what is in a subject: `https://127.0.0.1:5000/api/subjects?q=scheme:form`.

Each subject is a separate vocabulary, but does not have its own API route.

To add to a subject: `uv run invenio rdm-records add-to-fixture form`. This appears to run over all our vocabularies even if only one is specified.

Subject term IDs cannot be shared across schemes.

Questions:

- What does adding to a subject look like? Add term to yaml, run `add-to-fixture`?
- How can we remove a term from a subject?
  - If we remove a term, what happens to records that use that term?
- How can we update a term (e.g. change its label) in a subject?
  - If we update a term, what happens to records that use that term?
