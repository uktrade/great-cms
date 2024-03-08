import json
import uuid

import requests
from django.conf import settings
from django.utils.crypto import get_random_string
from msal import ConfidentialClientApplication

# replace this with your email firstname.lastname
EMAIL_ADDRESS_TO_REPLACE = ""


def _get_access_token():
    app = ConfidentialClientApplication(
        client_id=settings.DYNAMICS_APPLICATION_ID,
        authority=f"https://login.microsoftonline.com/{settings.DYNAMICS_TENANT_ID}",
        client_credential=settings.DYNAMICS_CLIENT_SECRET,
        token_cache=None,
    )
    token_response = app.acquire_token_for_client(scopes=[f"{settings.DYNAMICS_INSTANCE_URI}/.default"])
    if "access_token" not in token_response:
        raise Exception("Failed to acquire token")

    return token_response["access_token"]


def test_create_contact_with_email_sent():
    url = f"{settings.DYNAMICS_INSTANCE_URI}/api/data/v9.2/contacts"
    data = {
        "firstname": get_random_string(10),
        "lastname": get_random_string(20),
        "emailaddress1": "{EMAIL_ADDRESS_TO_REPLACE}@digital.trade.gov.uk",
        "adx_identity_emailaddress1confirmed": True,
        "ownerid@odata.bind": f"teams({settings.DYNAMICS_OWNING_TEAM_ID})",
    }

    response = requests.post(
        url,
        json=json.dumps(data, default=str),
        headers={
            "Authorization": f"Bearer {_get_access_token()}",
        },
    )
    assert response.status_code == 204


def test_create_bulk_contacts_with_emails_sent():

    contacts = []
    for cnt in range(1, 1000):
        data = {
            "firstname": get_random_string(10),
            "lastname": get_random_string(20),
            "emailaddress1": f"{EMAIL_ADDRESS_TO_REPLACE}+{cnt}@digital.trade.gov.uk",
            "adx_identity_emailaddress1confirmed": True,
            "ownerid@odata.bind": f"teams({settings.DYNAMICS_OWNING_TEAM_ID})",
            "donotbulkemail": False,
            "address1_country": None,
        }
        contacts.append(data)

    session = requests.Session()
    session.headers.update(dict(Authorization=f'Bearer {_get_access_token()}'))
    session.headers.update(
        {'OData-MaxVersion': '4.0', 'OData-Version': '4.0', 'If-None-Match': 'null', 'Accept': 'application/json'}
    )
    session.headers.update({"Prefer": "odata.continue-on-error"})

    batch_uri = f'{settings.DYNAMICS_INSTANCE_URI}/api/data/v9.2/$batch'
    request_uri = '/api/data/v9.2/contacts'

    base_preamble = (
        """
Content-Type: application/http
Content-Transfer-Encoding: binary

POST """
        + request_uri
        + """ HTTP/1.1
Content-Type: application/json; type=entry

"""
    )

    boundary = f"batch_{str(uuid.uuid4())}"
    session.headers.update({"Content-Type": f'multipart/mixed; boundary="{boundary}"'})
    boundary = ("--" + boundary).encode()
    preamble = boundary + base_preamble.encode()
    body = "".encode()
    for contact in contacts:
        body = body + preamble + json.dumps(contact).encode()
    body = body + "\n".encode() + boundary + "--".encode()
    req = requests.Request(
        'POST',
        batch_uri,
        data=body,
        headers=session.headers,
    ).prepare()

    response = session.send(req)
    assert response.status_code == 204
