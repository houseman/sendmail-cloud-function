import os
import pytest
import re


def test_get_env(mocker):
    # Patch os.environ.get
    mock_env_vars = {"ONE": "ONE", "TWO": "2", "THREE": "3"}
    mocker.patch.dict(os.environ, mock_env_vars, clear=True)

    from send_mail.config import get_env_int, get_env_str

    assert get_env_str("ONE") == "ONE"
    assert get_env_int("TWO") == 2
    assert get_env_str("THREE") == "3"
    assert get_env_int("FOUR") == 0
    assert get_env_str("FIVE", "5") == "5"
    assert get_env_int("SIX", 6) == 6

    with pytest.raises(
        ValueError, match=re.escape("invalid literal for int() with base 10: 'ONE'")
    ):
        get_env_int("ONE")
