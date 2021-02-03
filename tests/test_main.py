def test_salepen_send_mail(mocker, mock_event, mock_context):
    import main
    from cloudfunc.controllers import Controller
    from cloudfunc.models import ControllerResponse

    response = ControllerResponse(message="OK", response_code=200)
    mocker.patch.object(Controller, "send", return_value=response)
    output = main.cloud_send_mail(mock_event, mock_context)
    assert output == ("OK", 200)
