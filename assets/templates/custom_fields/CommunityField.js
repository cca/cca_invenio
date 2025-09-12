// field is only visible when record is submitted to a particular community
import {useFormikContext} from "formik"
import React, {useState, useEffect} from "react"
// redux store getState().deposit.editorState.selectedCommunity is the only way to know the selected community
import {useSelector} from "react-redux"
import {TextField} from "react-invenio-forms"

const CommunityField = ({ fieldPath, ...props }) => {
    const {setFieldValue} = useFormikContext()
    const community = useSelector(state => state.deposit.editorState.selectedCommunity?.slug)
    const [active, setActive] = useState(community === 'test')

    useEffect(() => {
        const isActive = (community === 'test')
        const newKey = `communityfield-${community}` // ! does this do anything?
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
        helpText={props.description}
        label={props.label}
    />
}

export default CommunityField
