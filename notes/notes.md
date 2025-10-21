# General Notes on InvenioRDM

## Example Sites

| Site | URL | Repos | Notes |
|------|-----|-------|-------|
| CalTech Data | https://data.caltech.edu/ | https://github.com/caltechlibrary/caltechdata | see their [scripts](https://github.com/caltechlibrary/caltechdata/tree/main/scripts) & [api](https://github.com/caltechlibrary/caltechdata_api/) |
| CalTech Authors | https://authors.library.caltech.edu/ | https://github.com/caltechlibrary/caltechauthors | |
| TU Wien | https://researchdata.tuwien.ac.at/ | https://gitlab.tuwien.ac.at/fairdata/invenio-theme-tuw | |
| TU Graz | https://repository.tugraz.at/ | https://github.com/tu-graz-library/invenio-theme-tugraz | |
| CERN Document Server | https://repository.cern/ | https://github.com/CERNDocumentServer/cds-rdm | bleeding edge v12 |
| Zenodo | https://zenodo.org/ | https://github.com/zenodo/zenodo-rdm | useful [cli commands](https://github.com/zenodo/zenodo-rdm/blob/master/site/zenodo_rdm/cli.py) |
| Northwestern Medicine | https://prism.northwestern.edu/ | no github repo? | |
| BIG-MAP Archive | https://archive-capex.energy.dtu.dk/ | https://github.com/team-capex/big-map-archive |
| Knowledge Commons | https://works.hcommons.org/ | https://github.com/MESH-Research/knowledge-commons-works | great [dev docs](https://github.com/MESH-Research/knowledge-commons-works/tree/main/docs/source/developing) |

## [Documentation](https://inveniordm.docs.cern.ch/)

The most important sections of the documentation are **[Customize](https://inveniordm.docs.cern.ch/operate/customize/)** and **[Reference](https://inveniordm.docs.cern.ch/reference/)**. **[Maintain and Develop](https://inveniordm.docs.cern.ch/maintenance/)** is less useful in general (unless we decide to write custom modules or contribute to the main project) but establishes some fundamental concepts and nuances, like how records and communities function.

## Roadmap

More detailed roadmap with an issue for each feature: https://github.com/inveniosoftware/product-rdm/issues

There are also issue queues on individual modules, especially for bugs. Major features tend to start on the product-rdm repo then transfer to a module when their requirements are defined.

High-level roadmap (less useful): https://inveniosoftware.org/products/rdm/roadmap/

### Digital Preservation

OCFL is being worked on but right now there is only a tool to export Invenio files to OCFL, they are not stored in that layout. Still, their layout is _similar_ — files are stored in venv root > /var/instance/data > then a tree like this:
├── 1b
│   └── 3c
│       └── 2deb-40cd-46ed-9097-0b44fc0aa2ef
│           └── data

#### File Integrity Check

We may not use this feature with cloud storage. It probably conflicts with GSB autoclass, which is going to be a vital cost-saving measure.

The v11 file integrity check report is wonderful, something obviously missing from EQUELLA. It took me some time to figure out what the `CELERY_BEAT_SCHEDULE` settings had to look like (see celery_beat.py in the code_samples dir):

```python
from datetime import timedelta
from invenio_app_rdm.config import CELERY_BEAT_SCHEDULE
CELERY_BEAT_SCHEDULE = {
    **CELERY_BEAT_SCHEDULE,
    'file-checks': {
        'task': 'invenio_files_rest.tasks.schedule_checksum_verification',
        'schedule': timedelta(seconds=60),
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
        'schedule': timedelta(seconds=120)
    }
}
```

This sets the check to run every minute and the report to mail every other minute, if you then enter into the instance data dir and mess with one of the files (e.g. `echo 'blah' >> 1b/3c/2deb-40cd-46ed-9097-0b44fc0aa2ef/data`) it'll trigger the check and print an email to your console.
