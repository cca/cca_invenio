# Request JSON report on program admins from Workday
import json
from os import environ

import click
import requests
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials

report_url = "https://wd5-services1.myworkday.com/ccx/service/customreport2/cca/cca_int/Current_Academic_Program_Leadership?format=json"


def get_secret(
    project_id: str = "cca-integrations", secret_id: str = "data_pipeline_workday"
) -> str:
    """Retrieve the latest version of the password from Google Secret Manager."""
    GSM_CREDENTIALS: Credentials | None = None
    if environ.get("GSM_CREDENTIALS"):
        GSM_CREDENTIALS: Credentials | None = Credentials.from_service_account_info(
            json.loads(environ["GSM_CREDENTIALS"])
        )

    if GSM_CREDENTIALS:
        client = secretmanager.SecretManagerServiceClient(credentials=GSM_CREDENTIALS)
    else:
        client = secretmanager.SecretManagerServiceClient()

    secret_name: str = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response: secretmanager.AccessSecretVersionResponse = client.access_secret_version(
        request={"name": secret_name}
    )

    return response.payload.data.decode("UTF-8")


def program_admins_report(
    username: str,
    password: str,
    url: str = report_url,
):
    """Download the program admins report from Workday."""
    if not username or not password:
        raise ValueError("Username and password must be provided.")

    headers: dict[str, str] = {"Accept": "application/json"}

    # HTTP auth request
    response: requests.Response = requests.get(
        url, headers=headers, auth=(username, password)
    )
    response.raise_for_status()

    return response.json()


@click.command()
@click.option(
    "--url",
    help="The URL of the Workday report.",
    default=environ.get("PROGRAM_ADMINS_REPORT_URL", report_url),
)
@click.option(
    "--username",
    help="The Workday ISU username.",
    default=environ.get("ISU_USERNAME", ""),
)
def main(url, username):
    """Download and print the program admins report from Workday. Requires an Integrated Systems User (ISU) account. The username can be set via ISU_USERNAME environment variable. The password is retrieved from Google Secret Manager (cca-integrations/data_pipeline_workday). Contact the Integrations Engineer for credentials."""
    password: str = get_secret()
    if not password:
        click.echo(
            "Error: unable to retrieve Workday ISU password from Secret Manager. Check that the service account or current user has access."
        )
        exit(1)
    report = program_admins_report(username, password, url)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
