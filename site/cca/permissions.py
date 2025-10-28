from flask_principal import RoleNeed
from invenio_administration.generators import Administration
from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy
from invenio_records_permissions.generators import Generator, IfConfig, SystemProcess
from invenio_records_permissions.policies.records import RecordPermissionPolicy
from invenio_search.engine import dsl


# Provide role=library access to OBJECT (multiple types) if cca:archives_series exists
class LibraryStaffIfArchives(Generator):
    def needs(self, record=None, **kwargs):
        # print("LibraryStaffIfArchives needs locals", locals())
        if not record:
            return [RoleNeed("library")]
        if record.get("custom_fields", {}).get("cca:archives_series"):
            return [RoleNeed("library")]
        # "record" is actually a community, no better way to identify it?
        # we could write different generator for comm perm policy
        if "communities" in record.get("$schema"):
            return [RoleNeed("library")]
        return []

    def query_filter(self, identity=None, **kwargs):  # type: ignore
        # print("LibraryStaffIfArchives query_filter locals", locals())
        if identity is None:
            return []
        for need in identity.provides:
            # RoleNeed objects have method == "role" and value == role name
            if getattr(need, "method", None) == "role" and need.value == "library":
                return dsl.Q("exists", field="custom_fields.cca:archives_series")
        return []


# Only allow admins to create communities
# TODO eventually there'll be a Community Creator role we can give only to admins
# TODO https://github.com/inveniosoftware/rfcs/issues/90
# https://discord.com/channels/692989811736182844/704625518552547329/1296091404409372763
class CCACommunityPermissionPolicy(CommunityPermissionPolicy):
    """Custom community permission policy to only allow admins to create communities."""

    # Override can_create permission. Previous definition:
    # can_create = [AuthenticatedUser(), SystemProcess()]
    can_create = [Administration(), SystemProcess()]

    # Since this action uses an action we override, it must also be updated.
    # Otherwise it would use the `can_create` from the base permission policy.
    can_create_restricted = [
        IfConfig("COMMUNITIES_ALLOW_RESTRICTED", then_=can_create, else_=[]),
    ]

    # without this library staff cannot see records with cca:archives_series fields
    # in restricted communities that they're not a member of
    can_read = CommunityPermissionPolicy.can_read + [LibraryStaffIfArchives()]


class CCARDMRecordPermissionPolicy(RDMRecordPermissionPolicy):
    can_read = RDMRecordPermissionPolicy.can_read + [LibraryStaffIfArchives()]
    can_read_files = RDMRecordPermissionPolicy.can_read_files + [
        LibraryStaffIfArchives()
    ]
    # I do not think the below is necessary as RDM.can_search = can_all
    can_search = RDMRecordPermissionPolicy.can_search + [LibraryStaffIfArchives()]
    can_view = RDMRecordPermissionPolicy.can_view + [LibraryStaffIfArchives()]


# not sure if this has any effect, cannot see records in /api/records?q=... queries
class CCARecordPermissionPolicy(RecordPermissionPolicy):
    can_read = RecordPermissionPolicy.can_read + [LibraryStaffIfArchives()]
    can_read_files = RecordPermissionPolicy.can_read_files + [LibraryStaffIfArchives()]
