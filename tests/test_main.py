from responses import ControllerResponse


def test_cloud_send_mail(mocker, mock_event, mock_context):
    import google.cloud.logging

    from function import controllers as ControllersModule

    mocker.patch.object(ControllersModule, "SendController")
    mocker.patch.object(google.cloud.logging, "Client")

    # Mock the `SendController` class
    mock_controller = mocker.Mock()
    mock_controller.send.return_value = ControllerResponse(
        message="OK", response_code=200
    )

    import main
    from main import cloud_send_mail

    main.controller = mock_controller

    output = cloud_send_mail(mock_event, mock_context)

    assert output == ("OK", 200)
