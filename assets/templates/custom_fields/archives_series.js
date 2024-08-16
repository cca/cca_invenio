import React, {Component} from "react"

import {Input} from "react-invenio-forms"
import {Grid} from "semantic-ui-react"


export class ArchivesSeries extends Component {
    render() {
        const {
            fieldPath, // injected by the custom field loader via the `field` config property
            series,
            subseries,
        } = this.props
        return (
            <Grid>
                <Grid.Column width="8">
                    {/* https://github.com/inveniosoftware/react-invenio-forms/blob/master/src/lib/forms/widgets/text/Input.js */}
                    <Input
                        description="The Archives series."
                        fieldPath={`${fieldPath}.series`}
                        icon="folder"
                        label={series.label}
                        placeholder={series.placeholder}
                    ></Input>
                </Grid.Column>
                <Grid.Column width="8">
                    <Input
                        description="The Archives subseries."
                        fieldPath={`${fieldPath}.subseries`}
                        label={subseries.label}
                        placeholder={subseries.placeholder}
                    ></Input>
                </Grid.Column>
            </Grid>
        )
    }
}
