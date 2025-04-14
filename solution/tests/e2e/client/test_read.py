from uuid import uuid4

from aiohttp import ClientSession

from tests.e2e.models import ClientModel
from tests.e2e.status import NOT_FOUND, OK


async def test_read_existing(
    http_session: ClientSession,
    url: str,
    created_clients: list[ClientModel],
) -> None:
    client = created_clients[0]
    client_id = client.client_id
    endpoint = f"{url}/clients/{client_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == OK
        client_data = ClientModel(**(await response.json()))
        assert client_data == client


async def test_read_nonexistent(
    http_session: ClientSession,
    url: str,
) -> None:
    non_existent_id = str(uuid4())
    endpoint = f"{url}/clients/{non_existent_id}"
    async with http_session.get(endpoint) as response:
        assert response.status == NOT_FOUND
