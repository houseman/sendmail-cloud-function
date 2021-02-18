from datetime import datetime

import pytest


@pytest.fixture()
def mock_transaction(mocker):
    mock_transaction = mocker.Mock()
    mock_transaction.begin.return_value = mocker.Mock()

    return mock_transaction


@pytest.fixture()
def mock_entity(mocker):
    mock_entity = mocker.Mock()
    mocker.patch.object(mock_entity, "update")

    return mock_entity


@pytest.fixture()
def mock_client(mocker):
    mock_client = mocker.Mock()
    mocker.patch.object(mock_client, "put")
    mock_client.key.return_value = mocker.Mock()
    mock_client.get.return_value = None

    return mock_client


def test_start(mocker, mock_transaction):
    from cloudfunc.utils import TransactionUtil
    from google.cloud import datastore

    mocker.patch.object(datastore, "Client")
    mock_call = mocker.patch.object(
        TransactionUtil._client, "transaction", return_value=mock_transaction
    )

    TransactionUtil()._start()

    mock_call.assert_called()


def test_commit(mocker, mock_entity, mock_transaction):
    from cloudfunc.models import TransactionRecord
    from cloudfunc.utils import TransactionUtil

    ts = datetime.now()
    tr = TransactionRecord(try_count=1, completed_at=ts)
    tu = TransactionUtil()
    tu._entity = mock_entity
    tu._transaction = mock_transaction

    mock_update = mocker.patch.object(tu._entity, "update")
    mock_put = mocker.patch.object(tu._client, "put")
    mock_commit = mocker.patch.object(tu._transaction, "commit")

    tu.commit(tr)

    mock_update.assert_called()
    mock_put.assert_called()
    mock_commit.assert_called()


@pytest.mark.parametrize(
    "entity_get", [({"try_count": 1, "completed_at": datetime.now()}), (None)]
)
def test_create_entity(mocker, mock_client, entity_get):
    from cloudfunc.utils import TransactionUtil

    tu = TransactionUtil()

    # _get = {"try_count": 1, "completed_at": ts}
    mock_client.get.return_value = entity_get

    tu._client = mock_client

    output = tu.create_entity("TestEntity", 1234567890)

    if entity_get:
        assert output.try_count == entity_get.get("try_count")
        assert output.completed_at == entity_get.get("completed_at")
    else:
        assert output.try_count == 0
        assert output.completed_at is None
