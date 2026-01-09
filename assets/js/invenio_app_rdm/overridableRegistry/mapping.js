/**
 * Override Invenio React Components https://inveniordm.docs.cern.ch/operate/customize/look-and-feel/override_components/
 * Example from Zenodo:
 * https://github.com/zenodo/zenodo-rdm/blob/master/assets/js/invenio_app_rdm/overridableRegistry/mapping.js#L3
 * Find the names of overridable components by running `reactOverridableEnableDevMode()` in dev tools
 * TODO we need to find a way to include the invenio_app_rdm default override (TimelineFeedHeader)
 * It's not in a JS package, is copying a bunch of files the only way?
 */

import {RelatedWorksIfLibraries} from "../../components/LibrariesConditionalFields";

export const overriddenComponents = {
    "InvenioAppRdm.Deposit.AccordionFieldFunding.container": () => null,
    "InvenioAppRdm.Deposit.LanguagesField.container": () => null,
    "InvenioAppRdm.Deposit.VersionField.container": () => null,
    "InvenioAppRdm.Deposit.PublisherField.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldAlternateIdentifiers.container": () => null,
    // TODO look into conditional container that shows this for Libraries community records
    "InvenioAppRdm.Deposit.AccordionFieldRelatedWorks.container": RelatedWorksIfLibraries,
    "InvenioAppRdm.Deposit.AccordionFieldReferences.container": () => null,
    "InvenioCommunities.CommunityProfileForm.AccordionField.MetadataFunding": () => null
}
