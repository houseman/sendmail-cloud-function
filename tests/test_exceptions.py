import pytest


def test_mail_server_response_error():
    from exceptions import ApiResponseError

    error = ApiResponseError(status_code=400, message="Test")

    assert error.status_code == 400
    assert error.message == "Test"
    assert str(error) == "[400] Test"


def test_api_response_error(mocker, mock_message_object):
    import requests
    from controllers import Controller
    from exceptions import ApiResponseError

    controller = Controller()
    mocker.patch.object(requests, "post", side_effect=Exception("mocked error"))
    with pytest.raises(ApiResponseError):
        controller._send_to_api(mock_message_object)
