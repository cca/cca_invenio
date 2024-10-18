// field is only visible when record is submitted to a particular community
import React, {Component} from "react"
import {TextField} from "react-invenio-forms"

// ! Neither the values from useFormikContext nor the record from the props tell you what community the record is in.
// ! We can only look for ?community=id in the URL which is only present when the record is submitted to a particular community.
export class CommunityField extends Component {
    render() {
        const {fieldPath} = this.props
        const community = new URLSearchParams(window.location.search).get("community")

        if (community === 'test') {
            return <TextField
                fieldPath={fieldPath}
                helpText="This field is only visible when record is submitted to the Test Community."
                label="Community-specific Field"
            />
        }
        return null
    }
}

export default CommunityField
