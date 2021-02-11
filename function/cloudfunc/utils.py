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

    _transaction: Transaction
    _entity: Entity

    def start(self) -> TransactionUtil:
        """
        Create a Google Cloud Datastore `Transaction`
        """
        logging.info("Begin transaction")
        self._transaction = self._client.transaction()
        self._transaction.begin()

        return self

    def commit(self, transaction: TransactionRecord) -> None:
        """
        Commit the current tranaction to the datastore, using state from the given
        `TransactionRecord` instance.
        """
        logging.info(f"Commit transaction: {transaction.__dict__}")
        self._entity.update(transaction.__dict__)
        self._client.put(self._entity)
        self._transaction.commit()

    def create_entity(self, kind: str, key_id: Union[int, str]) -> TransactionRecord:
        """
        Create or retrieve a datastore entity and set values into
        a model `TransactionRecord` instance that will hold state.
        """

        key: Key = self._client.key(kind, key_id)

        self._entity = self._client.get(key)

        if not self._entity:
            # Create the Entity if the key doesnot exist
            self._entity = Entity(key)

        return TransactionRecord(
            try_count=self._entity.get("try_count") or 0,
            completed_at=self._entity.get("completed_at"),
        )
