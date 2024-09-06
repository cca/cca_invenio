import React, {Component} from "react"
import {TextField} from "react-invenio-forms"

// Input only renders if the Invenio record is of a certain resource type
export class ConditionalField extends Component {
    constructor(props) {
        super(props)
        const resourceType = this.props?.record?.metadata?.resource_type?.id
        this.state = {
            active: resourceType ? resourceType.toString().startsWith("publication") : false,
            interval: setInterval(() => {
                const resourceType = this.props?.record?.metadata?.resource_type?.id
                if (this.state.resourceType === resourceType) return
                this.setState({
                    active: resourceType ? resourceType.toString().startsWith("publication") : false,
                    resourceType: resourceType,
                })
                this.forceUpdate()
                clearInterval(this.state.interval)
            }, 2000),
            key: this.props.fieldPath + resourceType,
            resourceType: resourceType,
        }
    }

    componentWillUnmount() {
        clearInterval(this.state.interval)
    }

    render() {
        const {
            fieldPath, // injected by the custom field loader via the `field` config property
        } = this.props

        // return text field only for publication types
        return (
            <TextField
                className={this.state.active ? "" : "d-none"}
                description="Enter the publication title. This field only appears for publication resources."
                disabled={!this.state.active}
                fieldPath={fieldPath}
                key={this.state.key}
                label="Publication title"
            />
        )
    }
}

export default ConditionalField
