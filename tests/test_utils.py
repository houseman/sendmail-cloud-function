import pytest


def test_attribute_exception():
    from exceptions import PayloadError
    from utils import create_message_from_payload

    with pytest.raises(PayloadError):
        create_message_from_payload({})
