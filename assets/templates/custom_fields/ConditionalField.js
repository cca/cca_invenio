import {Component} from "react"

import {TextField} from "react-invenio-forms"

// Input only renders if the Invenio record is of a certain resource type

export class ConditionalField extends Component {
    render() {
        const {
            fieldPath, // injected by the custom field loader via the `field` config property
        } = this.props

        // return text field only for all publication types
        if (this.props.record.resource_type.id.startsWith("publication")) {
            return (
                <TextField
                    description="Enter the publication title. This field only appears for publication resources."
                    fieldPath={fieldPath}
                    // ? add resource_type.id to the key to force re-render when resource_type changes
                    // key={fieldPath + this.props.record.resource_type.id}
                    label="Publication title"
                    optimized
                    required
                />
            )
        }
        return ""
    }
}

export default ConditionalField
