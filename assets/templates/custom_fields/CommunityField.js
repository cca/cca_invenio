// field is only visible when record is submitted to a particular community
import {useFormikContext} from "formik"
import React, {useState, useEffect} from "react"
// redux store getState().deposit.editorState.selectedCommunity is the only way to know the selected community
import {useSelector} from "react-redux"
import {TextField} from "react-invenio-forms"

const CommunityField = ({fieldPath}) => {
    const {setFieldValue} = useFormikContext()
    const community = useSelector(state => state.deposit.editorState.selectedCommunity?.slug)
    const [active, setActive] = useState(community === 'test')
    console.log("Initial state", community, active)

    useEffect(() => {
        console.log("useEffect state", community, active)
        const isActive = (community === 'test')
        const newKey = `communityfield-${community}`
        if (active !== isActive) {
            setActive(isActive)
            // clear the field value when it becomes inactive
            if (!isActive) setFieldValue(fieldPath, "")
        }
    }, [community, active, fieldPath, setFieldValue])

    return <TextField
        className={active ? "" : "d-none"}
        disabled={!active}
        fieldPath={fieldPath}
        helpText="This field is only visible when record is submitted to the Test Community."
        label="Community-specific Field"
    />
}

export default CommunityField
