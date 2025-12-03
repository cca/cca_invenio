import os

from requests import Session

token = os.getenv("TOKEN") or os.getenv("INVENIO_TOKEN", "")
http = Session()
http.headers.update({"Authorization": f"Bearer {token}"})
http.headers.update({"Content-Type": "application/json"})
http.verify = False

id = "1970-1979"
subject = {
    "id": id,
    "scheme": "time",
    "subject": id,
}
r = http.put(f"https://127.0.0.1:5000/api/subjects/{id}", json=subject)
print(id, r.status_code)
