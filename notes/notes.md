# General Notes on InvenioRDM

## Example Sites

| Site | URL | Repos | Notes |
|------|-----|-------|-------|
| CalTech | https://data.caltech.edu/ | https://github.com/caltechlibrary/caltechdata | see their CLI commands
| TU Wien | https://researchdata.tuwien.ac.at/ | https://gitlab.tuwien.ac.at/fairdata/invenio-theme-tuw |
| TU Graz | https://repository.tugraz.at/ | https://github.com/tu-graz-library/invenio-theme-tugraz |
| ITAM | https://invenio.itam.cas.cz/ |
| CERN Document Server | not live yet | https://github.com/CERNDocumentServer/cds-rdm | bleeding edge v12
| Zenodo | not live yet? | https://github.com/zenodo/zenodo-rdm | bleeding edge v12, useful [cli commands](https://github.com/zenodo/zenodo-rdm/blob/master/site/zenodo_rdm/cli.py)

## Documentation

https://inveniordm.docs.cern.ch/

The most important sections of the documentation are **[Customize](https://inveniordm.docs.cern.ch/customize/)** and **[Reference](https://inveniordm.docs.cern.ch/reference/)**. **[Develop](https://inveniordm.docs.cern.ch/develop/)** is less useful in general (unless we decide to write custom modules or contribute to the main project) but establishes some fundamental concepts and nuances, like how records and communities function.

The documentation for some concepts is spread across multiple sections. For instance, Custom Fields has [a quickstart guide](https://inveniordm.docs.cern.ch/customize/metadata/custom_fields/records/) under Customize, lists of potential field and [UI widgets](https://inveniordm.docs.cern.ch/reference/custom_fields/widgets/) under Reference, and a [how-to guide](https://inveniordm.docs.cern.ch/develop/howtos/custom_fields/) under Develop that goes deeper to cover creating a custom UI widget.

## Roadmap

High-level roadmap: https://inveniosoftware.org/products/rdm/roadmap/

More detailed roadmap with an issue for each feature: https://github.com/inveniosoftware/product-rdm/issues

### Digital Preservation

OCFL is being worked on but right now there is only a tool to export Invenio files to OCFL, they are not stored in that layout. Still, their layout is _similar_ — files are stored in venv root > /var/instance/data > then a tree like this:
├── 1b
│   └── 3c
│       └── 2deb-40cd-46ed-9097-0b44fc0aa2ef
│           └── data

#### File Integrity Check

The v11 file integrity check report is wonderful, something obviously missing from EQUELLA. It took me some time to figure out what the `CELERY_BEAT_SCHEDULE` settings had to look like (see celery_beat.py in this dir):

```python
from datetime import datetime
from invenio_app_rdm.config import CELERY_BEAT_SCHEDULE
CELERY_BEAT_SCHEDULE = {
    **CELERY_BEAT_SCHEDULE,
    'file-checks': {
        'task': 'invenio_files_rest.tasks.schedule_checksum_verification',
        'schedule': datetime.timedelta(seconds=60),
        'kwargs': {
            'batch_interval': {
                'hours': 1
            },
            'frequency': {
                'days': 14
            },
            'max_count': 0,
            'files_query': 'invenio_app_rdm.utils.files.checksum_verification_files_query'
        }
    },
    'file-integrity-report': {
        'task': 'invenio_app_rdm.tasks.file_integrity_report',
        'schedule': datetime.timedelta(seconds=120)
    }
}
```

This sets the check to run every minute and the report to mail every other minute, if you then enter into the instance data dir and mess with one of the files (e.g. `echo 'blah' >> 1b/3c/2deb-40cd-46ed-9097-0b44fc0aa2ef/data`) it'll trigger the check and print an email to your console.
