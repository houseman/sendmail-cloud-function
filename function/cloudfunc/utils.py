from __future__ import annotations

import logging
from typing import Union

from cloudfunc.models import TransactionRecord
from google.cloud import datastore
from google.cloud.datastore.entity import Entity
from google.cloud.datastore.key import Key
from google.cloud.datastore.transaction import Transaction


class TransactionUtil:
    _client = datastore.Client()
    _entity: Entity
    _transaction: Transaction

    def commit(self, transaction_log: TransactionRecord) -> None:
        """
        Commit the current tranaction to the datastore, using state from the given
        `TransactionRecord` instance.
        """
        logging.info(f"Commit transaction: {transaction_log}")
        self._entity.update(transaction_log.to_dict())
        self._client.put(self._entity)
        self._transaction.commit()

    def create_entity(self, kind: str, key_id: Union[int, str]) -> TransactionRecord:
        """
        Create or retrieve a datastore entity and set values into
        a model `TransactionRecord` instance that will hold state.
        """
        self._transaction = self._start()

        key: Key = self._client.key(kind, key_id)

        self._entity = self._client.get(key)

        if not self._entity:
            # Create the Entity if the key doesnot exist
            self._entity = Entity(key)

        return TransactionRecord(
            try_count=self._entity.get("try_count", 0),
            completed_at=self._entity.get("completed_at", None),
        )

    def _start(self) -> Transaction:
        """
        Create a Google Cloud Datastore `Transaction`
        """
        logging.info("Begin transaction")
        _transaction = self._client.transaction()
        _transaction.begin()

        return _transaction
