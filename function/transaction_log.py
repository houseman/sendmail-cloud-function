from google.cloud import datastore

from datetime import datetime

from typing import Optional


class TransactionLog:
    _datastore_client: Optional[datastore.Client] = None

    def __init__(self) -> None:
        if not self._datastore_client:
            # Instantiates a client
            self._datastore_client = datastore.Client()

    def create(self, id: int) -> datastore.Entity:
        with self._datastore_client.transaction():
            key = self._datastore_client.key("TransactionLog", id)

            transaction_log = self._datastore_client.get(key)

            if not transaction_log:
                # Create the Entity
                transaction_log = datastore.Entity(key)

            return transaction_log

    def complete(self, transaction: datastore.Entity):
        self._datastore_client.put(transaction)
