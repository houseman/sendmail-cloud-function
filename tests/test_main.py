import pytest

from function.cloudfunc.models import ControllerResponse


@pytest.mark.parametrize(
    "response, expected",
    [
        (ControllerResponse(message="OK", response_code=200), ("OK", 200)),
        (ControllerResponse(message="ERROR", response_code=500), ("OK", 200)),
    ],
)
def test_cloud_send_mail(mocker, response, expected, mock_event, mock_context):
    from function.cloudfunc import config as ConfigModule
    from function.cloudfunc import controllers as ControllersModule

    # Mock the `Controller` class
    mock_controller = mocker.Mock()
    mock_controller.send.return_value = response
    mocker.patch.object(ControllersModule, "Controller", return_value=mock_controller)

    # Mock the `Config` class
    mock_logger = mocker.Mock()
    mock_config = mocker.Mock()
    mock_config.create_logger.return_value = mock_logger
    mocker.patch.object(ConfigModule, "Config", return_value=mock_config)

    from function.main import cloud_send_mail

    output = cloud_send_mail(mock_event, mock_context)

    assert output == expected
