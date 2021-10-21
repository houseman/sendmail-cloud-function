def test_send(mocker, mock_ok_response, mock_message_object):
    import requests

    from function.integrations import Mailgun
    from function.responses import ApiResponse

    mock_session = mocker.Mock()
    mock_session.post.return_value = mock_ok_response
    mocker.patch.object(requests, "Session", return_value=mock_session)

    response = Mailgun().send(mock_message_object)

    assert response == ApiResponse(message="OK", response_code=200)
