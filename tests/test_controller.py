import pytest
import base64
import json

from models import MailMessage


@pytest.fixture()
def mock_context(mocker):
    mock_context = mocker.Mock()
    mock_context.event_id = "617187464135194"
    mock_context.timestamp = "2019-07-15T22:09:03.761Z"

    return mock_context


@pytest.fixture()
def mock_message():
    return dict(
        rcpt="info@example.com",
        sender="test@example.com",
        subject="Test subject",
        html_content="<h1>Test Message</h1><p>Test HTML message</p>",
        text_content="Test plain text",
    )


@pytest.fixture
def mock_message_json(mock_message):
    return json.dumps(mock_message)


@pytest.fixture
def mock_message_encoded(mock_message_json):
    return base64.b64encode(mock_message_json.encode("utf-8")).decode("utf-8")


@pytest.fixture()
def mock_event(mock_message_encoded):
    return {"attributes": {}, "data": mock_message_encoded}


@pytest.fixture
def mock_message_object(mocker):
    return MailMessage(
        recipient="info@example.com",
        sender="test@example.com",
        subject="Test subject",
        html_content="<h1>Test Message</h1><p>Test HTML message</p>",
        text_content="Test plain text",
    )


def test_send_to_api(mocker, mock_message_object):
    import requests
    from controllers import Controller

    request_result = mocker.Mock()
    request_result.status_code = 200
    request_result.text = "OK"

    mocker.patch.object(requests, "post", return_value=request_result)

    controller = Controller()
    output = controller._send_to_api(mock_message_object)

    assert output.response_code == 200


def test_get_message_from_payload(mock_event, mock_message_object):
    from controllers import Controller

    controller = Controller()
    output = controller._get_message_from_payload(mock_event)
    assert output == mock_message_object
