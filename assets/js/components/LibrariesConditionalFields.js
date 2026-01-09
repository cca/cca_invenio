import {useFormikContext} from "formik"
import React, {useState, useEffect} from "react"
// redux store getState().deposit.editorState.selectedCommunity is the only way to know the selected community
import {useSelector} from "react-redux"
import {AccordionField} from "react-invenio-forms"
import {RelatedWorksField} from "@js/invenio_rdm_records"
import {i18next} from "@translations/invenio_app_rdm/i18next"
// https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm/deposit/RDMDepositForm.js
// https://github.com/inveniosoftware/invenio-rdm-records/tree/master/invenio_rdm_records/assets/semantic-ui/js/invenio_rdm_records/src/deposit/fields

// Config for the related works section
const severityChecks = {
    info: {
        label: i18next.t("Recommendation"),
        description: i18next.t("This check is recommended but not mandatory.")
    },
    error: {
        label: i18next.t("Error"),
        description: i18next.t("This check indicates a critical issue that must be addressed.")
    }
}

/**
 * Whether the given community is one of the "Libraries" communities
 * @param {string} community - community slug
 * @returns {boolean}
 */
function isLibrariesCommunity(community) {
    return [
        'artists-books',
        'art-collection',
        'capp-street',
        'hamaguchi',
        'libraries',
        'mudflats',
        'open-access',
        'design-book-review',
        'faculty-research']
        .includes(community)
}

export const RelatedWorksIfLibraries = (props) => {
    const fieldPath = "metadata.related_identifiers"
    // we override the accordion field so we have to re-implement it here
    // props.vocabularies contains the vocabularies from RDMDepositForm
    const vocabularies = props.vocabularies || {}
    const community = useSelector(state => state.deposit.editorState.selectedCommunity?.slug)
    const active = isLibrariesCommunity(community)

    if (!active) return null

    return <AccordionField
        includesPaths={[fieldPath]}
        severityChecks={severityChecks}
        active
        label={i18next.t("Related works")}
        id="related-works-section">
        <RelatedWorksField
            fieldPath={fieldPath}
            options={vocabularies.metadata.identifiers}
            showEmptyValue
        />
    </AccordionField>
}
