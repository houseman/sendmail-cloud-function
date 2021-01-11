import pytest

import base64
import json


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


def test_event_contains_no_data(mocker, context):
    from main import salepen_send_mail

    (message, result) = salepen_send_mail({}, context)
    assert result == 400


def test_event_contains_bad_data(mocker, context):
    from main import salepen_send_mail

    (message, result) = salepen_send_mail({"data": "foobar"}, context)
    assert result == 400


def test_send_message_request(mocker, event, context):
    import requests
    from main import salepen_send_mail

    request_result = mocker.Mock()
    request_result.status_code = 200
    request_result.text = "OK"

    mocker.patch.object(requests, "post", return_value=request_result)

    (message, result) = salepen_send_mail(event, context)
    assert result == 200
