from datetime import datetime

import pytest
from cloudfunc.models import ApiResponse, TransactionRecord


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
    "transaction_record, api_response",
    [
        (
            TransactionRecord(try_count=3),
            ApiResponse(
                response_code=429,
                message="Message ID 617187464135194 previously completed",
            ),
        ),
        (
            TransactionRecord(try_count=0, completed_at=None),
            ApiResponse(response_code=200, message="OK"),
        ),
        (
            TransactionRecord(try_count=1, completed_at=datetime.now()),
            ApiResponse(
                response_code=429,
                message="Message ID 617187464135194 previously completed",
            ),
        ),
    ],
)
def test_send_message(
    mocker, transaction_record, api_response, mock_message_object, mock_context
):
    from cloudfunc.controllers import Controller

    controller = Controller()
    mocker.patch.object(
        controller._tu, "create_entity", return_value=transaction_record
    )
    mocker.patch.object(controller._tu, "commit")

    mocker.patch.object(controller, "_send_to_api", return_value=api_response)

    output = controller._send_message(mock_message_object, mock_context)

    assert output == api_response


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
