"""Script to create communities. Since this uses the REST API to create
communities, it does not need to be run in the Flask app context and
thus is not available under the `invenio cca` commands."""

import os
from pathlib import Path
from typing import Any, Literal, Optional

import click
import yaml
from pydantic import BaseModel, HttpUrl


class CommunityAccess(BaseModel):
    member_policy: Literal["closed", "open"]
    record_policy: Literal["closed", "open"]
    visibility: Literal["public", "restricted"]


class CommunityType(BaseModel):
    id: Literal["event", "organization", "project", "topic"]
    title: Optional[dict[str, str]] = None  # en: English Name


class CommunityMetadata(BaseModel):
    curation_policy: Optional[str] = None
    description: Optional[str] = None
    # ROR ID or name string
    organizations: Optional[list[dict[Literal["id", "name"], str]]] = None
    title: str
    type: CommunityType
    website: Optional[HttpUrl] = None


class Community(BaseModel):
    access: CommunityAccess
    metadata: CommunityMetadata
    slug: str  # TODO slug validation? no spaces?


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--file",
    default=Path("app_data") / "communities.yaml",
    help="YAML file of communities.",
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "-t",
    "--token",
    default=lambda: os.getenv("TOKEN") or os.getenv("INVENIO_TOKEN", ""),
    help="Administrator personal access token.",
    type=str,
)
def create_communities(file: Path, token: str):
    """Create communities from a YAML file. Requires an Invenio personal access token, which it looks for in the TOKEN or INVENIO_TOKEN env vars."""
    with open(file, "r") as fh:
        communities: list[dict[str, Any]] = yaml.safe_load(fh)

    if not isinstance(communities, list):
        click.echo("ERROR: communities yaml is not a list, exiting", err=True)
        exit(1)

    if not token:
        click.echo("ERROR: requires an Invenio personal access token.", err=True)
        exit(1)

    for community in communities:
        Community(**community)  # validate the data
        click.echo(f"{community['metadata']['title']} community passed validation")
        # TODO create using the REST API


if __name__ == "__main__":
    create_communities()
