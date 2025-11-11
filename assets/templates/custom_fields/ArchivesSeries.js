import React, {Component} from "react"

import {Dropdown, FieldLabel, SelectField} from "react-invenio-forms"
import {Grid} from "semantic-ui-react"

// Archives Series is a hierarchical controlled vocab
// selection of first series determines subseries options
// ! Sync with vault_miration/migrate/archives_series.json
const archivesSeries = {
    "I. Administrative Materials": [
        "1. Academic Council",
        "2. Accreditation and Licensing Materials",
        "3. Board of Directors",
        "4. Faculty Assembly / Faculty Senate",
        "5. Faculty and Staff Files",
        "6. Finance and Development",
        "7. General Admin Files",
        "8. Partnerships and Affiliations",
        "9. Presidents Office"
    ],
    "II. Alumni Society Materials": [
        "1. Alumni Files",
        "2. Alumni Exhibitions"
    ],
    "III. College Life": [
        "1. Commencement Materials",
        "2. Ephemera",
        "3. Events",
        "4. Awards",
        "5. Oral Histories"
    ],
    "IV. Department Materials": [
        "1. Academic Departments",
        "2. Admin Departments",
        "3. Other"
    ],
    "V. Exhibits and the CCA Art Collection": [
        "1. Collection and Administration",
        "2. Exhibits",
        "3. Gallery Management Class"
    ],
    "VI. Photographs": [
        "1. Commencement",
        "2. Students",
        "3. Alumni",
        "4. Department/Studio",
        "5. Events",
        "6. Exhibits",
        "7. Works of art",
        "8. Photos by format"
    ],
    "VII. Press": [
        "1. Press Clippings",
        "2. Press Releases"
    ],
    "VIII. Periodicals and Other Publications": [
        "1. College",
        "2. Student",
        "3. Alumni",
        "4. Yearbooks",
        "5. Issued an ISBN/ISSN",
        "6. Catalogs/ Schedule of classes"
    ],
    "X. Buildings and Grounds": [
        "1. Berkeley",
        "2. Oakland",
        "3. San Francisco",
        "4. Other Locations"
    ]
}

export class ArchivesSeries extends Component {
    constructor(props) {
        super(props)
        this.state = {
            series: "",
        }
    }

    render() {
        const {
            fieldPath, // injected by the custom field loader via the `field` config property
            icon,
            series,
            subseries,
        } = this.props

        return (
            <Grid>
                <Grid.Column width="8">
                    {/* https://github.com/inveniosoftware/react-invenio-forms/blob/master/src/lib/forms/SelectField.js */}
                    {/* Do we have to use a SelectField because Dropdown doesn't expose blur or change handlers?!? */}
                    <SelectField
                        aria-label={series.label}
                        clearable
                        // description={`${series.description} 3`}
                        defaultValue={""} // this.state.seriesValue?
                        fieldPath={`${fieldPath}.series`}
                        label={<FieldLabel htmlFor={fieldPath} icon={icon} label={series.label} />}
                        // event arg is essentially useless, no non-null properties
                        onBlur={(event, component) => {
                            this.setState({series: component.field.value })
                        }}
                        options={Object.keys(archivesSeries).map(s => (
                            { key: s, text: s, value: s }
                        ))}
                        placeholder={series.placeholder}
                    />
                    {series.description && <label className="helptext">{series.description}</label>}
                </Grid.Column>
                <Grid.Column width="8">
                    {/* https://github.com/inveniosoftware/react-invenio-forms/blob/master/src/lib/forms/widgets/select/Dropdown.js */}
                    <Dropdown
                        description={subseries.description}
                        // disabled if we don't have a series
                        disabled={this.state.series == ""}
                        fieldPath={`${fieldPath}.subseries`}
                        icon={icon}
                        key={`${this.state.series} subseries`} // force re-render when series changes
                        label={subseries.label}
                        options={archivesSeries[this.state.series] ? archivesSeries[this.state.series].map(s => (
                            {id: s, title_l10n: s}
                        )) : []}
                        placeholder={subseries.placeholder}
                        required={this.state.series != ""}
                    />
                </Grid.Column>
            </Grid>
        )
    }
}

export default ArchivesSeries
