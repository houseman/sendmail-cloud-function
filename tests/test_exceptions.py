import pytest


def test_mail_server_response_error():
    from send_mail.exceptions import ApiException

    error = ApiException(status_code=400, message="Test")

    assert error.status_code == 400
    assert error.message == "Test"
    assert str(error) == "[400] Test"


def test_api_response_error(mocker, mock_message_object):
    import requests
    from send_mail.exceptions import ApiException
    from send_mail.integrations import MailgunIntegration

    mock_session = mocker.Mock()
    mock_response = mocker.Mock()
    mocker.patch.object(
        mock_session,
        "post",
        side_effect=requests.exceptions.HTTPError(response=mock_response),
    )
    mocker.patch.object(requests, "Session", return_value=mock_session)

    with pytest.raises(ApiException):
        MailgunIntegration().send(mock_message_object)
