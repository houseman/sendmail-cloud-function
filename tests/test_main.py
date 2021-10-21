import pytest

from function.responses import ControllerResponse


@pytest.mark.parametrize(
    "controller_response, expected",
    [
        (ControllerResponse(message="OK", response_code=200), ("OK", 200)),
        (
            ControllerResponse(message="Forbidden", response_code=401),
            ("Forbidden", 401),
        ),
    ],
)
def test_cloud_send_mail(
    mocker, controller_response, expected, mock_event, mock_context
):
    from function import controllers as ControllersModule

    mocker.patch.object(ControllersModule, "SendController")

    # Mock the `SendController` class
    mock_controller = mocker.Mock()
    mock_controller.send.return_value = controller_response

    from function import main
    from function.main import cloud_send_mail

    main.controller = mock_controller

    output = cloud_send_mail(mock_event, mock_context)

    assert output == expected
