import { useFormikContext } from "formik"
import React, { useState, useEffect } from "react"
import { TextField } from "react-invenio-forms"

const ConditionalField = ({ fieldPath }) => {
    const {values, setFieldValue} = useFormikContext()
    const [active, setActive] = useState(false)
    const [key, setKey] = useState('conditionalfield')

    useEffect(() => {
        const isActive = values.metadata.resource_type.startsWith("publication")
        const newKey = `conditionalfield-${values.metadata.resource_type}`
        if (active !== isActive) {
            setActive(isActive)
            // clear the field value when it becomes inactive
            if (!isActive) setFieldValue(fieldPath, "")
        }
        if (key !== newKey) setKey(newKey)
    }, [values, active, key, fieldPath, setFieldValue])

    return (
        <TextField
            className={active ? "" : "d-none"}
            disabled={!active}
            fieldPath={fieldPath}
            helpText="Enter the publication title. This field only appears for publication resources."
            key={key}
            label="Publication title"
        />
    )
}

export default ConditionalField
