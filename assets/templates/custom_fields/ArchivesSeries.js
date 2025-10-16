import React, {Component} from "react"

import {Dropdown, FieldLabel, SelectField} from "react-invenio-forms"
import {Grid} from "semantic-ui-react"

// Archives Series is a hierarchical controlled vocab
// selection of first one determines options for second one
// TODO fill out vocab using CCA/C Archives Box List sheet
// TODO https://github.com/cca/cca_invenio/issues/63
const archivesSeries = {
    "I. Administrative Materials": [
        "2. Accreditation and Licensing Materials",
        "3. Board of Directors and Trustees",
        "4. Faculty Assembly and Faculty Senate"
    ],
    "II. Alumni Society Materials": ["2. Alumni Files"],
    "III. College Life": [
        "1. Commencement Materials",
        "2. Ephemera",
        "3. Events",
        "5. Oral Histories",
    ],
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
