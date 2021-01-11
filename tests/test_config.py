import pytest

import google.auth


@pytest.mark.parametrize("secret_string", [("secret"), ("Something else")])
def test_get_mailgun_api_sending_key(mocker, secret_string):
    from google.cloud import secretmanager_v1

    from config import Config

    mocker.patch.object(google.auth, "default", return_value=(None, "project-id"))
    mocker.patch.object(
        secretmanager_v1, "SecretManagerServiceClient", return_value=mocker.Mock()
    )

    payload = mocker.Mock()
    payload.data = mocker.Mock()
    mocker.patch.object(payload.data, "decode", return_value=secret_string)
    access_secret_version = mocker.Mock()
    access_secret_version.payload = payload

    mocker.patch.object(
        Config.secret_manager,
        "access_secret_version",
        return_value=access_secret_version,
    )

    config = Config()

    expected = secret_string
    output = config._get_mailgun_api_sending_key()

    assert output == expected


def test_get_mailgun_api_sending_key_exception(mocker):
    with pytest.raises(Exception):
        assert test_get_mailgun_api_sending_key(mocker, None)


def test_get_mailgun_api_sending_key_exceptions(mocker):
    from google.auth.exceptions import DefaultCredentialsError
    from google.api_core.exceptions import PermissionDenied

    from google.cloud import secretmanager_v1

    from config import Config

    mocker.patch.object(
        google.auth, "default", side_effect=DefaultCredentialsError("Foo")
    )
    with pytest.raises(Exception):
        assert Config()

    mocker.patch.object(google.auth, "default", return_value=(None, "project-id"))
    mocker.patch.object(
        secretmanager_v1,
        "SecretManagerServiceClient",
        side_effect=PermissionDenied("Foo"),
    )
    with pytest.raises(Exception):
        assert Config()


def test_create_logger(mocker):
    import google.cloud.logging

    from google.auth.exceptions import DefaultCredentialsError

    from config import Config

    logging_client = mocker.Mock()
    mocker.patch.object(logging_client, "get_default_handler")
    mocker.patch.object(logging_client, "setup_logging")

    mocker.patch.object(google.cloud.logging, "Client", return_value=logging_client)

    output = Config().create_logger()

    assert output == logging_client

    mocker.patch.object(
        google.cloud.logging, "Client", side_effect=DefaultCredentialsError("Foo")
    )
    with pytest.raises(Exception):
        assert Config().create_logger()
