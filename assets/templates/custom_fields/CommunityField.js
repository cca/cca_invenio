// field is only visible when record is submitted to a particular community
import React from "react"
import React from "react"
import React, {useState, useEffect} from "react"
import {TextField} from "react-invenio-forms"

// I believe this needs to be a class component and then use something in the props
// passed to the constructor to determine what community it's in.
export class CommunityField extends Component {
    constructor(props) {
        super(props)
        this.state = {
            community: this.props.community || this.props.record.community || "",
        }
    }

    render() {this.state.community == "community-id" &&
        <TextField
            fieldPath={fieldPath}
            helpText="This field is only visible when record is submitted to a particular community."
            label="Community-specific Field"
        />
    }
}

export default CommunityField
