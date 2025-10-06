"""Script to create communities. Since this uses the REST API to create
communities, it does not need to be run in the Flask app context and
thus is not available under the `invenio cca` commands."""

import os
from pathlib import Path
from typing import Any

import click
import urllib3
import yaml
from cca.models import Community
from requests import Response, Session


def community_exists(http: Session, host: str, slug: str) -> bool:
    """Check if a community with the given slug exists."""
    r: Response = http.get(f"https://{host}/api/communities/{slug}")
    if r.status_code == 200:
        click.echo(
            f"Community https://{host}/communities/{slug} already exists, skipping"
        )
        return True
    elif r.status_code == 404:
        return False
    else:
        click.echo(
            f"ERROR: checking for existing community '{slug}' returned status code {r.status_code}, exiting",
            err=True,
        )
        exit(1)


def create_community(http: Session, host: str, community: dict[str, Any]) -> None:
    """Create a community using the REST API."""
    r: Response = http.post(f"https://{host}/api/communities", json=community)
    if r.status_code == 201:
        click.echo(f"Created community {community['metadata']['title']}")
    else:
        click.echo(
            f"ERROR HTTP {r.status_code}: creating community '{community['metadata']['title']}'",
            err=True,
        )
        click.echo(r.text, err=True)
        exit(1)


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--file",
    default=Path("app_data") / "communities.yaml",
    help="YAML file of communities (default: app_data/communities.yaml).",
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--host",
    default=lambda: os.getenv("HOST") or os.getenv("INVENIO_HOST", ""),
    help="Hostname of Invenio instance (e.g. invenio-dev.cca.edu)",
    type=str,
)
@click.option(
    "-n",
    "--no-verify",
    help="Disable SSL verification (use during local testing).",
    is_flag=True,
)
@click.option(
    "-t",
    "--token",
    default=lambda: os.getenv("TOKEN") or os.getenv("INVENIO_TOKEN", ""),
    help="Administrator personal access token.",
    type=str,
)
def create_communities(file: Path, host: str, no_verify: bool, token: str):
    """Create communities from a YAML file. Requires an Invenio personal access token, which it looks for in the TOKEN or INVENIO_TOKEN env vars. The domain of the Invenio instance can be specified with the --host flag or using HOST or INVENIO_HOST env vars."""
    with open(file, "r") as fh:
        communities: list[dict[str, Any]] = yaml.safe_load(fh)

    if not isinstance(communities, list):
        click.echo("ERROR: communities yaml is not a list, exiting", err=True)
        exit(1)

    if not token:
        click.echo("ERROR: requires an Invenio personal access token.", err=True)
        exit(1)

    # setup the HTTP session
    http = Session()
    http.headers.update({"Authorization": f"Bearer {token}"})
    http.headers.update({"Content-Type": "application/json"})
    if no_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        http.verify = False

    for community in communities:
        Community(**community)  # validate the data first

        if not community_exists(http, host, community["slug"]):
            create_community(http, host, community)


if __name__ == "__main__":
    create_communities()
