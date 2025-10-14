from flask_principal import RoleNeed
from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy
from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl

# this turned out to be irrelevant I think, RMD uses RDMRecordPermissionPolicy
# from invenio_records_permissions.policies.records import RecordPermissionPolicy


class LibraryStaffIfArchives(Generator):
    def needs(self, record=None, **kwargs):
        print("LibraryStaffIfArchives needs locals", locals())
        if not record:
            return [RoleNeed("library")]
        if record.get("custom_fields", {}).get("cca:archives_series"):
            return [RoleNeed("library")]
        # "record" is actually a community, not better way to identify it?
        # we could write different generator for comm perm policy
        if "communities" in record.get("$schema"):
            return [RoleNeed("library")]
        return []

    def query_filter(self, identity=None, **kwargs):  # type: ignore
        # ?  do we need to add `if identity.has_role("library"):`?
        print("LibraryStaffIfArchives query_filter locals", locals())
        return dsl.Q("exists", field="custom_fields.cca:archives_series")


class CCARDMRecordPermissionPolicy(RDMRecordPermissionPolicy):
    can_read = RDMRecordPermissionPolicy.can_read + [LibraryStaffIfArchives()]
    can_read_files = RDMRecordPermissionPolicy.can_read_files + [
        LibraryStaffIfArchives()
    ]
    # can_search = RDMRecordPermissionPolicy.can_search + [LibraryStaffIfArchives()]
    can_view = RDMRecordPermissionPolicy.can_view + [LibraryStaffIfArchives()]
