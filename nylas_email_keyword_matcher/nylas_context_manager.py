from nylas import APIClient
from nylas.client.errors import NylasError
import logging


logger = logging.Logger(__file__)


class NylasContextManager:

    def __init__(self, **client_kwargs):
        self._client_kwargs = client_kwargs
        self.is_valid_client()

    def is_valid_client(self) -> bool:
        try:
            self._make_api_client()
            self._delete_api_client()
            return True
        except Exception as e:
            raise NylasError from e

    def __enter__(self) -> APIClient:
        return self._make_api_client()

    def _make_api_client(self) -> APIClient:
        try:
            client = APIClient(**self._client_kwargs)
            logger.info(f'Nylas client created from account id {client.account["id"]}')
            self._api_client = client
            return self._api_client
        except Exception as e:
            raise NylasError from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delete_api_client()

    def _delete_api_client(self):
        del self._api_client
        self._api_client = None
