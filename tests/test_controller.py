from datetime import datetime

import pytest


def test_send_to_api(mocker, mock_message_object):
    import requests
    from cloudfunc.controllers import Controller

    request_result = mocker.Mock()
    request_result.status_code = 200
    request_result.text = "OK"

    mocker.patch.object(requests, "post", return_value=request_result)

    controller = Controller()
    output = controller._send_to_api(mock_message_object)

    assert output.response_code == 200


def test_get_message_from_payload(mock_event, mock_message_object):
    from cloudfunc.controllers import Controller

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
    from cloudfunc.controllers import Controller
    from google.cloud import datastore

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
    from cloudfunc.controllers import Controller
    from cloudfunc.models import ApiResponse, ControllerResponse

    controller = Controller()

    api_response = ApiResponse(message="OK", response_code=200)

    mocker.patch.object(controller, "_send_message", return_value=api_response)
    output = controller.send(mock_event, mock_context)

    assert output == ControllerResponse(message="OK", response_code=200)


def test_attribute_exception():
    from cloudfunc.controllers import Controller
    from cloudfunc.exceptions import PayloadError

    controller = Controller()

    with pytest.raises(PayloadError):
        controller._get_message_from_payload({})


def test_bad_send(mock_context):
    from cloudfunc.controllers import Controller

    controller = Controller()

    with pytest.raises(Exception):
        controller.send({"data": ""}, mock_context)
