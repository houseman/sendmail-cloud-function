import pytest


def test_mail_server_response_error():
    from function.cloudfunc.exceptions import ApiResponseError

    error = ApiResponseError(status_code=400, message="Test")

    assert error.status_code == 400
    assert error.message == "Test"
    assert str(error) == "[400] Test"


def test_api_response_error(mocker, mock_message_object, mock_context):
    import requests

    from function.cloudfunc.controllers import Controller
    from function.cloudfunc.exceptions import ApiResponseError

    controller = Controller()
    mocker.patch.object(requests, "post", side_effect=Exception("mocked error"))
    with pytest.raises(ApiResponseError):
        controller._send_message(mock_message_object, mock_context)
