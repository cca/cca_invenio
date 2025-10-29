# README

This directory contains static fixtures that are ingested when the app is initialized. _Updating the data here does not update the corresponding data in the app_. For that, use `invenio rdm-records add-to-fixture` or `invenio vocabularies update`.

The **pages** folder is for [static pages](https://inveniordm.docs.cern.ch/operate/customize/static_pages/).

The **vocabularies** folder is for the various types of [vocabularies](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/#vocabularies). These cover more functions than you might expect, including resource types and subjects. There are different types of vocabs and they may be structured differently. We can also create custom vocabs which are used by custom fields, but they must use an existing vocabulary type (usually subject?).

Many default vocabularies are in the [invenio-rdm-records](https://github.com/inveniosoftware/invenio-rdm-records) repository under the fixtures > data > [vocabularies](https://github.com/inveniosoftware/invenio-rdm-records/tree/master/invenio_rdm_records/fixtures/data/vocabularies) directory.
