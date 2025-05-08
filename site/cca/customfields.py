from typing import Any
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.config import RDM_FACETS, RDM_SEARCH
from invenio_records_resources.services.records.facets import CFTermsFacet
from invenio_records_resources.services.custom_fields import BaseCF, TextCF
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
            **kwargs,
        )

    # BaseCF must implement field property
    @property
    def field(self):
        """Marshmallow field for custom fields."""
        return fields.Dict()

    @property
    def mapping(self):
        """Search mapping"""
        return {
            "properties": {
                # We can't have these be keywords with their roman numeral prefixes
                "series": {"type": "text"},
                "subseries": {"type": "text"},
            }
        }


# Associated course information, see a course data file for available fields
# And site/cca/cli.py for how to load this data into OpenSearch
class CourseCF(BaseCF):
    """{
    "colocated_sections": ["COURSE_SECTION-3-42783"],
    "department": "Architecture",
    "department_code": "ARCHT",
    "instructors_string": "Frida Kahlo, Jean-Paul Sartre",
    "instructors": [
        { "first_name": "Frida", "last_name": "Kahlo", "middle_name": "", "username": "fkahlo", "employee_id": "500101", "uid": "1001001" },
        { "first_name": "Jean-Paul", "last_name": "Sartre", "middle_name": "", "username": "jpsatre", "employee_id": "500102", "uid": "1001002" }
    ],
    "section": "ARCHT-1000-1",
    "section_calc_id": "ARCHT-1000-1_AP_Fall_2025",
    "section_refid": "COURSE_SECTION-3-42782",
    "term": "Fall 2025",
    "title": "Architecture 1" }"""

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_args=dict(
                colocated_sections=fields.List(SanitizedUnicode()),
                department=SanitizedUnicode(),
                department_code=SanitizedUnicode(),
                instructors_string=SanitizedUnicode(),
                instructors=fields.Nested(
                    {
                        "first_name": SanitizedUnicode(),
                        "last_name": SanitizedUnicode(),
                        "middle_name": SanitizedUnicode(),
                        "username": SanitizedUnicode(),
                        "employee_id": SanitizedUnicode(),
                        "uid": SanitizedUnicode(),
                    }
                ),
                section=SanitizedUnicode(),
                section_calc_id=SanitizedUnicode(),
                section_refid=SanitizedUnicode(),
                term=SanitizedUnicode(),
                title=SanitizedUnicode(),
            ),
            **kwargs,
        )

    # BaseCF must implement field property
    @property
    def field(self) -> fields.Dict:
        """Marshmallow field for custom fields."""
        return fields.Dict()

    @property
    def mapping(self):
        """Search mapping."""
        return {
            "properties": {
                "colocated_sections": {"type": "keyword"},
                "department": {"type": "text"},
                "department_code": {"type": "keyword"},
                "instructors_string": {"type": "text"},
                "instructors": {
                    "type": "nested",
                    "properties": {
                        "first_name": {"type": "text"},
                        "last_name": {"type": "text"},
                        "middle_name": {"type": "text"},
                        "username": {"type": "keyword"},
                        "employee_id": {"type": "keyword"},
                        "uid": {"type": "keyword"},
                    },
                },
                "section": {"type": "keyword"},
                "section_calc_id": {"type": "keyword"},
                "section_refid": {"type": "keyword"},
                "term": {"type": "text"},
                "title": {"type": "text"},
            }
        }


RDM_NAMESPACES: dict[str, str] = {
    "cca": "https://libraries.cca.edu/",
}

RDM_CUSTOM_FIELDS: list[BaseCF] = [
    ArchivesSeriesCF(name="cca:archives_series"),
    CourseCF(name="cca:course"),
    # TODO these example fields can eventually be removed
    TextCF(name="cca:community_field"),
    TextCF(name="cca:conditional_field"),
    VocabularyCF(  # the type of custom field, VocabularyCF is a controlled vocabulary
        dump_options=True,  # True when the list of all possible values will be visible in the dropdown UI component, typically for small vocabularies
        multiple=False,  # if the field accepts a list of values (True) or single value (False)
        name="cca:program",  # name of the field, namespaced by `cca`
        vocabulary_id="programs",  # controlled vocabulary id defined in the vocabularies.yaml file
    ),
]

RDM_CUSTOM_FIELDS_UI: list[dict[str, Any]] = [
    {
        "section": _("CCA Custom Fields"),
        "fields": [
            # ! When I add this I get an error that CourseField.js cannot be found by any loader
            {
                "field": "cca:course",
                "template": "course.html",
                # "ui_widget": "CourseField",
                "ui_widget": None,
                "props": {},
            },
            {
                "field": "cca:conditional_field",
                "template": "conditional_field.html",
                "ui_widget": "ConditionalField",
                # props hard-coded into ConditionalField.js
                "props": {},
            },
            {
                "field": "cca:community_field",
                "template": "community_field.html",
                "ui_widget": "CommunityField",
                # props hard-coded into CommunityField.js
                "props": {},
            },
            {
                "field": "cca:program",
                "ui_widget": "AutocompleteDropdown",
                "template": "program.html",
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
                "template": "archives_series.html",
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

RDM_FACETS: dict[str, dict[str, Any]] = {
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

RDM_SEARCH: dict[str, list[str]] = {
    **RDM_SEARCH,
    "facets": RDM_SEARCH["facets"] + ["program"],
}
