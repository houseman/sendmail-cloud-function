import os


def test_get_env_val(mocker):
    # Patch os.environ.get
    mock_env_vars = {"ONE": "1", "TWO": "2", "THREE": "3"}
    mocker.patch.dict(os.environ, mock_env_vars, clear=True)

    from config import get_env_val

    assert os.environ["ONE"] == mock_env_vars["ONE"]
    assert get_env_val("TWO") == mock_env_vars["TWO"]
    assert get_env_val("THREE") == "3"
    assert get_env_val("FOUR") is None
    assert get_env_val("FIVE", "5") == "5"
