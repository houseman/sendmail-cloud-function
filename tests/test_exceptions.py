def test_mail_server_response_error():
    from exceptions import ApiResponseError

    error = ApiResponseError(status_code=400, message="Test")

    assert error.status_code == 400
    assert error.message == "Test"
    assert str(error) == "[400] Test"
