from typing import Any

from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.contrib.journal import (
    JOURNAL_CUSTOM_FIELDS,
    JOURNAL_CUSTOM_FIELDS_UI,
    JOURNAL_NAMESPACE,
)
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


# Custom Field options: https://github.com/inveniosoftware/invenio-records-resources/tree/master/invenio_records_resources/services/custom_fields
class ArchivesSeriesCF(BaseCF):
    """Archives Series and Subseries custom field
    { "series": "II. College Life", "subseries": "3. Events"}"""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_args=dict(series=SanitizedUnicode(), subseries=SanitizedUnicode()),
            **kwargs,
        )

    # BaseCF must implement field property
    @property
    def field(self):  # type: ignore
        """Marshmallow field for custom fields."""
        return fields.Dict()

    # BaseCF must implement search mapping
    @property
    def mapping(self) -> dict[str, Any]:  # type: ignore
        """Return the mapping."""
        return {
            "properties": {
                "series": {"type": "text"},
                "subseries": {"type": "text"},
            }
        }


# We also use journal custom fields for OA & DBR records
# https://inveniordm.docs.cern.ch/reference/metadata/#journal

RDM_NAMESPACES: dict[str, str | None] = {
    "cca": "https://libraries.cca.edu/",
    **JOURNAL_NAMESPACE,
}

RDM_CUSTOM_FIELDS: list[BaseCF] = [
    ArchivesSeriesCF(name="cca:archives_series"),
    *JOURNAL_CUSTOM_FIELDS,
]

RDM_CUSTOM_FIELDS_UI: list[dict[str, Any]] = [
    JOURNAL_CUSTOM_FIELDS_UI,
    {
        "section": _("CCA Fields"),
        "fields": [
            {
                "field": "cca:archives_series",
                "template": "archivesseries.html",
                "ui_widget": "ArchivesSeries",
                "props": {
                    "icon": "archive",
                    "series": {
                        "description": _(
                            "Only CCA/C Archives items require this field."
                        ),
                        "label": _("Archives Series"),
                        "placeholder": _("Archives Series"),
                    },
                    "subseries": {
                        "description": _("Select a Series to see Subseries."),
                        "label": _("Archives Subseries"),
                        "placeholder": _("Archives Subseries"),
                    },
                },
            },
        ],
    },
]

# TODO do we want to expose facets?
# https://inveniordm.docs.cern.ch/operate/customize/metadata/custom_fields/records/#search
