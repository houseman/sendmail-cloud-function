def test_send(mocker, mock_ok_response, mock_message_object):
    import requests
    from send_mail.integrations import Mailgun
    from send_mail.responses import ApiResponse

    mock_session = mocker.Mock()
    mock_session.post.return_value = mock_ok_response
    mocker.patch.object(requests, "Session", return_value=mock_session)

    response = Mailgun().send(mock_message_object)

    assert response == ApiResponse(message="OK", response_code=200)
