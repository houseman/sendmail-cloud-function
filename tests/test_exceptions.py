import pytest


def test_mail_server_response_error():
    from exceptions import ApiError

    error = ApiError(status_code=400, message="Test")

    assert error.status_code == 400
    assert error.message == "Test"
    assert str(error) == "[400] Test"


def test_api_response_error(mocker, mock_message_object):
    import requests
    from exceptions import ApiError
    from integrations import Mailgun

    mock_session = mocker.Mock()
    mocker.patch.object(mock_session, "post", side_effect=Exception("mocked error"))
    mocker.patch.object(requests, "Session", return_value=mock_session)

    with pytest.raises(ApiError):
        Mailgun().send(mock_message_object)
