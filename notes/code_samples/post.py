"""
POST record metadata and file to InvenioRDM REST API

See Invenio's example:
https://github.com/inveniosoftware/docs-invenio-rdm-restapi-example"""

import json
import os

import requests
import urllib3

# shut up urllib3 SSL verification warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

token = os.environ.get("TOKEN", False) or os.environ.get("INVENIO_TOKEN", False)
if not token:
    raise Exception(
        "Error: provide a personal access token in the TOKEN or INVENIO_TOKEN env var"
    )
# at least 5 HTTP requests to creating an item with a single attachment:
# 1) create metadata record as draft
# 2) create file area & add file names to draft
# 3) for each attachment
#   a) add file data to draft
#   b) commit the file to the draft
# 4) publish the draft


def result(response):
    print("HTTP {}".format(response.status_code))
    print(response.text)
    response.raise_for_status()


with open("./notes/code_samples/record.json", "r") as fh:
    data = json.load(fh)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    # create metadata-only draft
    response = requests.post(
        "https://127.0.0.1:5000/api/records", json=data, verify=False, headers=headers
    )

result(response)
draft = response.json()
id = draft["id"]

# add file names to draft
file_keys = [{"key": "syllabus.pdf"}]
response = requests.post(
    "https://127.0.0.1:5000/api/records/{}/draft/files".format(id),
    json=file_keys,
    headers=headers,
    verify=False,
)
result(response)

# PUT file data to draft
with open("./notes/code_samples/syllabus.pdf", "rb") as file:
    headers["Content-Type"] = "application/octet-stream"
    response = requests.put(
        "https://127.0.0.1:5000/api/records/{}/draft/files/{}/content".format(
            id, "syllabus.pdf"
        ),
        data=file,
        headers=headers,
        verify=False,
    )
    result(response)

# commit file
headers["Content-Type"] = "application/json"
response = requests.post(
    "https://127.0.0.1:5000/api/records/{}/draft/files/{}/commit".format(
        id, "syllabus.pdf"
    ),
    headers=headers,
    verify=False,
)
result(response)

# publish draft
response = requests.post(
    "https://127.0.0.1:5000/api/records/{}/draft/actions/publish".format(id),
    headers=headers,
    verify=False,
)
result(response)
# link to (HTML version of) published record
print(json.loads(response.text)["links"]["self_html"])
