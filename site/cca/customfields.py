from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.config import RDM_FACETS, RDM_SEARCH
from invenio_records_resources.services.records.facets import CFTermsFacet
from invenio_records_resources.services.custom_fields import BaseCF
from invenio_vocabularies.services.custom_fields import VocabularyCF
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
            **kwargs
        )

    # BaseCF must implement field property
    @property
    def field(self):
        """Marshmallow field for custom fields."""
        return fields.Dict()

    @property
    def mapping(self):
        """Return the mapping."""
        return {
            "properties": {
                "series": {"type": "text"},
                "subseries": {"type": "text"},
            }
        }


RDM_NAMESPACES = {
    "cca": "https://libraries.cca.edu/",
}

RDM_CUSTOM_FIELDS = [
    ArchivesSeriesCF(name="cca:archives_series"),
    VocabularyCF(  # the type of custom field, VocabularyCF is a controlled vocabulary
        dump_options=True,  # True when the list of all possible values will be visible in the dropdown UI component, typically for small vocabularies
        multiple=False,  # if the field accepts a list of values (True) or single value (False)
        name="cca:program",  # name of the field, namespaced by `cca`
        vocabulary_id="programs",  # controlled vocabulary id defined in the vocabularies.yaml file
    ),
]

RDM_CUSTOM_FIELDS_UI = [
    {
        "section": _("CCA Custom Fields"),
        "fields": [
            {
                "field": "cca:program",
                "template": "program.html",
                "ui_widget": "AutocompleteDropdown",
                "props": {
                    "autocompleteFrom": "/api/vocabularies/programs",
                    "autocompleteFromAcceptHeader": "application/vnd.inveniordm.v1+json",
                    "clearable": True,
                    "description": _("Select one of CCA's academic programs"),
                    "icon": "building",
                    "label": _("Academic Program"),
                    "multiple": False,  # True for selecting multiple values
                    "placeholder": _("Animation Program"),
                },
            },
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
    }
]

RDM_FACETS = {
    **RDM_FACETS,
    "program": {
        "facet": CFTermsFacet(  # backend facet
            field="cca:programs.id",  # id is the keyword field of a vocabulary
            label="Academic Program",
        ),
        "ui": {  # ui display
            "field": CFTermsFacet.field("cca:programs.id"),
        },
    },
}

RDM_SEARCH = {**RDM_SEARCH, "facets": RDM_SEARCH["facets"] + ["program"]}
