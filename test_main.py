import base64
import json
import os
import subprocess

import main

import pytest

import requests
from requests.packages.urllib3.util.retry import Retry

from dataclasses import dataclass

# SEE https://cloud.google.com/functions/docs/testing/test-background
# SEE https://github.com/GoogleCloudPlatform/functions-framework-python


@dataclass
class MailMessage:
    rcpt: str
    subject: str
    html_content: str
    text_content: str = None
    content_type: str = "text/html"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@pytest.fixture()
def context(mocker):
    mock_context = mocker.Mock()
    mock_context.event_id = "617187464135194"
    mock_context.timestamp = "2019-07-15T22:09:03.761Z"

    return mock_context


@pytest.fixture()
def mail_message():
    return MailMessage(
        rcpt="scott.houseman@gmail.com",
        subject="Test subject secret",
        html_content="<h1>Test Message</h1><p>Test HTML message</p>",
        text_content="Test plain text",
    )


@pytest.fixture
def mail_message_json(mail_message):
    return mail_message.toJSON()


@pytest.fixture
def mail_message_encoded(mail_message_json):
    return base64.b64encode(mail_message_json.encode("utf-8")).decode("utf-8")


@pytest.fixture()
def event(mail_message_encoded):
    return {"attributes": {}, "data": mail_message_encoded}


def test_salepen_send_mail_unit(mocker, event, context):
    main.salepen_send_mail(event, context)


def test_salepen_send_mail_integration(mocker, event, context):
    # sudo ufw allow from any to any port 8088 proto tcp
    port = 8088

    process = subprocess.Popen(
        [
            "functions-framework",
            "--target",
            "salepen_send_mail",
            "--signature-type",
            "event",
            "--port",
            str(port),
        ],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
    )

    # Send HTTP request simulating Pub/Sub message
    # (GCF translates Pub/Sub messages to HTTP requests internally)
    # SEE https://amalgjose.com/2020/02/27/gunicorn-connection-in-use-0-0-0-0-8000/#:~:text=One%20of%20the%20common%20error,with%20some%20other%20running%20process.&text=Some%20stale%20process%20is%20making%20the%20port%20busy.
    url = f"http://localhost:{port}/"

    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=retry_policy)

    session = requests.Session()
    session.mount(url, retry_adapter)

    response = session.post(url, json=event)
    print(response.text)

    assert response.status_code == 200

    # Stop the functions framework process
    process.kill()
    process.wait()
    out, err = process.communicate()

    print(out, err, response.content)
