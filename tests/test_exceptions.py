def test_mail_server_response_error():
    from exceptions import MailServerResponseError

    error = MailServerResponseError(status_code=400, text="Test")

    assert error.status_code == 400
    assert error.text == "Test"
    assert str(error) == "Test"
