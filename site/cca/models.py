from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl

"""These pydantic models of Invenio data types are used for validation only"""


class StrictBaseModel(BaseModel):
    # Forbid unknown/extra fields (Pydantic v2)
    model_config = ConfigDict(extra="forbid")


class CommunityAccess(StrictBaseModel):
    # can anyone request to join or do we control membership?
    member_policy: Literal["closed", "open"]
    # can anyone see the list of members or only members?
    members_visibility: Optional[Literal["public", "restricted"]] = None
    # closed really means "all records are restricted", closed comm cannot have public record
    record_policy: Literal["closed", "open"]
    # who can publish without review? Closed=no one, Open=Curators & up, Members=all members
    review_policy: Optional[Literal["closed", "members", "open"]] = None
    visibility: Literal["public", "restricted"]


class CommunityType(StrictBaseModel):
    id: Literal["event", "organization", "project", "topic"]
    title: Optional[dict[str, str]] = None  # en: English Name


class CommunityMetadata(StrictBaseModel):
    curation_policy: Optional[str] = None
    description: Optional[str] = None
    # ROR ID or name string
    organizations: Optional[list[dict[Literal["id", "name"], str]]] = None
    title: str
    type: CommunityType
    website: Optional[HttpUrl] = None


class Community(StrictBaseModel):
    access: CommunityAccess
    metadata: CommunityMetadata
    slug: str  # TODO slug validation? no spaces?


# TODO Course model for course custom-field


class UserProfile(BaseModel):
    # we require full_name
    affiliations: Optional[str] = None
    full_name: str


class User(BaseModel):
    # we require email & username
    active: Optional[bool] = None
    confirmed_at: Optional[datetime] = None
    email: EmailStr
    username: str  # TODO match username regex
    user_profile: UserProfile
