/**
 * Add here all the overridden components of your app.
 * Example from Zenodo:
 * https://github.com/zenodo/zenodo-rdm/blob/master/assets/js/invenio_app_rdm/overridableRegistry/mapping.js#L3
 * Find the names of overridable components in RDMDepositForm.js:
 * https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm/deposit/RDMDepositForm.js
 */

export const overriddenComponents = {
    "InvenioAppRdm.Deposit.AccordionFieldFunding.container": () => null,
    "InvenioAppRdm.Deposit.LanguagesField.container": () => null,
    "InvenioAppRdm.Deposit.VersionField.container": () => null,
    "InvenioAppRdm.Deposit.PublisherField.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldAlternateIdentifiers.container": () => null,
    // TODO look into conditional container that shows this for Libraries community records
    "InvenioAppRdm.Deposit.AccordionFieldRelatedWorks.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldReferences.container": () => null,
    "InvenioCommunities.CommunityProfileForm.AccordionField.MetadataFunding": () => null
}
