def test_constructor(mocker):
    import dotenv

    # Patch dotenv
    mock_env_vars = {"ONE": 1, "TWO": 2, "THREE": 3}
    mocker.patch.object(dotenv, "dotenv_values", return_value=mock_env_vars)

    from config import Config

    config = Config()

    assert config.get_val("ONE") == mock_env_vars["ONE"]
    assert config.get_val("TWO") == 2
    assert config.get_val("FOUR") is None
    assert config.get_val("FIVE", 5) == 5
