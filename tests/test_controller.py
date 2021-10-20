import pytest

from function.cloudfunc.models import ApiResponse


def test_send_to_api(mocker, mock_message_object):
    import requests

    from function.cloudfunc.controllers import Controller

    request_result = mocker.Mock()
    request_result.status_code = 200
    request_result.text = "OK"

    mocker.patch.object(requests, "post", return_value=request_result)

    controller = Controller()
    output = controller._send_message(mock_message_object)

    assert output.response_code == 200


def test_get_message_from_payload(mock_event, mock_message_object):
    from function.cloudfunc.controllers import Controller

    controller = Controller()
    output = controller._get_message_from_payload(mock_event)
    assert output == mock_message_object


@pytest.mark.parametrize(
    "api_response",
    [
        (
            ApiResponse(
                response_code=429,
                message="Message ID 617187464135194 previously completed",
            ),
        ),
        (ApiResponse(response_code=200, message="OK"),),
        (
            ApiResponse(
                response_code=429,
                message="Message ID 617187464135194 previously completed",
            ),
        ),
    ],
)
def test_send_message(mocker, api_response, mock_message_object, mock_context):
    from function.cloudfunc.controllers import Controller

    controller = Controller()

    mocker.patch.object(controller, "_send_message", return_value=api_response)

    output = controller._send_message(mock_message_object, mock_context)

    assert output == api_response


def test_send(mocker, mock_event, mock_context):
    from function.cloudfunc.controllers import Controller
    from function.cloudfunc.models import ApiResponse, ControllerResponse

    controller = Controller()

    api_response = ApiResponse(message="OK", response_code=200)

    mocker.patch.object(controller, "_send_message", return_value=api_response)
    output = controller.send(mock_event, mock_context)

    assert output == ControllerResponse(message="OK", response_code=200)


def test_attribute_exception():
    from function.cloudfunc.controllers import Controller
    from function.cloudfunc.exceptions import PayloadError

    controller = Controller()

    with pytest.raises(PayloadError):
        controller._get_message_from_payload({})


def test_bad_send(mock_context):
    from function.cloudfunc.controllers import Controller

    controller = Controller()

    with pytest.raises(Exception):
        controller.send({"data": ""}, mock_context)
