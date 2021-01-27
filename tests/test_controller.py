import pytest
import base64
import json

from datetime import datetime

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


@pytest.mark.parametrize(
    "transaction_log, response_code",
    [({}, 200), ({"completed_at": datetime.now()}, 429)],
)
def test_send_message(
    mocker, transaction_log, response_code, mock_message_object, mock_context
):
    from google.cloud import datastore

    from controllers import Controller

    controller = Controller()

    key = mocker.Mock()
    mocker.patch.object(controller._datastore_client, "key", return_value=key)

    mocker.patch.object(
        controller._datastore_client, "get", return_value=transaction_log
    )
    mocker.patch.object(controller._datastore_client, "put")
    mocker.patch.object(datastore, "Entity", return_value=transaction_log)

    output = controller._send_message(mock_message_object, mock_context)

    assert output.response_code == response_code


def test_send(mocker, mock_event, mock_context):
    from controllers import Controller
    from models import ApiResponse, ControllerResponse

    controller = Controller()

    api_response = ApiResponse(message="OK", response_code=200)

    mocker.patch.object(controller, "_send_message", return_value=api_response)
    output = controller.send(mock_event, mock_context)

    assert output == ControllerResponse(message="OK", response_code=200)
