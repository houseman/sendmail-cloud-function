import pytest
from send_mail.exceptions import ApiException, ControllerException
from send_mail.responses import ApiResponse, ControllerResponse


def test_send_success(mocker, mock_event):
    from send_mail import integrations as IntegrationsModule

    api_response = ApiResponse(message="OK", response_code=200)
    controller_response = ControllerResponse(message="OK", response_code=200)

    # Patch API connection
    mocker.patch.object(IntegrationsModule, "MailgunIntegration")

    mock_integration = mocker.Mock()
    mock_integration.send.return_value = api_response

    from send_mail.controllers import SendController

    controller = SendController()
    controller._integration = mock_integration
    output = controller.send(mock_event)

    assert output == controller_response


def test_send_error(mocker, mock_event):
    from send_mail import integrations as IntegrationsModule

    api_response = ApiException(message="Forbidden", status_code=401)

    # Patch API connection
    mocker.patch.object(IntegrationsModule, "MailgunIntegration")

    mock_integration = mocker.Mock()
    mock_integration.send.side_effect = api_response

    from send_mail.controllers import SendController

    controller = SendController()
    controller._integration = mock_integration

    with pytest.raises(ControllerException):
        controller.send(mock_event)


def test_attribute_exception():
    from send_mail.controllers import SendController
    from send_mail.exceptions import PayloadException

    with pytest.raises(PayloadException):
        SendController.get_message_from_payload({})


def test_bad_message():
    from send_mail.controllers import SendController

    controller = SendController()

    # Badly-formatted messages should not raise an exception as this will cause these to
    # be re-tried, which is not desireable.
    result = controller.send({"data": ""})
    assert result == ControllerResponse(message="Bad Request", response_code=400)
