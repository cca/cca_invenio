from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

"""These pydantic models of Invenio data types are used for validation only"""


class StrictBaseModel(BaseModel):
    # Forbid unknown/extra fields (Pydantic v2)
    model_config = ConfigDict(extra="forbid")


class CommunityAccess(StrictBaseModel):
    # can anyone request to join or do we control membership?
    member_policy: Literal["closed", "open"]
    # can anyone see the list of members or only members?
    members_visibility: Optional[Literal["public", "restricted"]] = None
    # who can submit, members only or everyone?
    record_policy: Literal["closed", "open"]
    # who can publish without review? Closed=no one, Open=Curators+, Members=all members
    review_policy: Optional[Literal["closed", "members", "open"]] = None
    # restricted = "all records are restricted", restricted community cannot have public records
    visibility: Literal["public", "restricted"]


class CommunityType(StrictBaseModel):
    id: Literal["event", "organization", "project", "topic"]
    title: Optional[dict[str, str]] = None  # en: English Name


class CommunityMetadata(StrictBaseModel):
    curation_policy: Optional[str] = None
    description: Optional[Annotated[str, Field(max_length=250)]] = None
    # ROR ID or name string
    organizations: Optional[list[dict[Literal["id", "name"], str]]] = None
    title: str
    type: CommunityType
    website: Optional[HttpUrl] = None


class Community(StrictBaseModel):
    access: CommunityAccess
    children: Optional[dict[Literal["allow"], bool]] = None
    metadata: CommunityMetadata
    slug: Annotated[str, Field(max_length=100, pattern=r"^[a-z0-9_-]+$")]


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
