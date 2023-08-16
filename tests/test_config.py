import os


def test_get_env_val(mocker):
    # Patch os.environ.get
    mock_env_vars = {"ONE": "1", "TWO": "2", "THREE": "3"}
    mocker.patch.dict(os.environ, mock_env_vars, clear=True)

    from send_mail.config import Config

    assert os.environ["ONE"] == mock_env_vars["ONE"]
    assert Config.get_env_val("TWO") == mock_env_vars["TWO"]
    assert Config.get_env_val("THREE") == "3"
    assert Config.get_env_val("FOUR") is None
    assert Config.get_env_val("FIVE", "5") == "5"
