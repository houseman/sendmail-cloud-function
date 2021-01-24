from proto import message
import pytest

import base64
import json


from dataclasses import dataclass

# SEE https://cloud.google.com/functions/docs/testing/test-background
# SEE https://github.com/GoogleCloudPlatform/functions-framework-python


@pytest.fixture()
def context(mocker):
    mock_context = mocker.Mock()
    mock_context.event_id = "617187464135194"
    mock_context.timestamp = "2019-07-15T22:09:03.761Z"

    return mock_context


@pytest.fixture()
def mail_message():
    return dict(
        rcpt="scott.houseman@gmail.com",
        subject="Test subject secret",
        html_content="<h1>Test Message</h1><p>Test HTML message</p>",
        text_content="Test plain text",
    )


@pytest.fixture
def mail_message_json(mail_message):
    return json.dumps(mail_message)


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
    from main import salepen_send_mail

    request_result = mocker.Mock()
    request_result.status_code = 200
    request_result.text = "OK"

    mocker.patch("main._send_message", return_value=request_result)
    (_, result) = salepen_send_mail(event, context)
    assert result == 200


@pytest.mark.parametrize(
    "transaction_log", [({}), ({"completed_at": "2019-07-15T22:09:03.761Z"})]
)
def test_send_message(mocker, mail_message, context, transaction_log):
    import requests
    from google.cloud import datastore
    from main import datastore_client, _send_message

    key = mocker.Mock()
    mocker.patch.object(datastore_client, "key", return_value=key)

    transaction_log = {}
    mocker.patch.object(datastore_client, "get", return_value=transaction_log)
    mocker.patch.object(datastore_client, "put")
    mocker.patch.object(datastore, "Entity", return_value=transaction_log)

    request_result = mocker.Mock()
    request_result.status_code = 200
    request_result.text = "OK"

    mocker.patch.object(requests, "post", return_value=request_result)

    output = _send_message(mail_message, context)
    assert output.status_code == 200
