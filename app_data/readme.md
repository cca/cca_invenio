# README

This directory contains static fixtures that are ingested when the app is initialized. _Updating the data here does not update the corresponding data in the app_. You must wipe and recreate the database to do so, but there is work being done on adding to pre-existing fixtures rather than recreating them.

The **pages** folder is for [static pages](https://inveniordm.docs.cern.ch/customize/static_pages/).

The **vocabularies** folder is for the various types of [vocabularies](https://inveniordm.docs.cern.ch/customize/vocabularies/). These cover more functions than you might expect, including resource types and subjects. There are different types of vocabs and they may be structured differently. You can also create custom vocabs which are used by custom fields, but they must use an existing vocabulary type (usually subject?).
