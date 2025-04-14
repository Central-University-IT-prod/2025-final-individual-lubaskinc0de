import pytest
from aiohttp import ClientSession

from tests.e2e.models import ClientModel
from tests.e2e.status import CREATED, UNPROCESSABLE_ENTITY

INVALID_CASES = [
    {"age": -1},
    {"age": 101},
]


async def test_bulk_create(
    http_session: ClientSession,
    url: str,
    valid_client_data: list[ClientModel],
) -> None:
    endpoint = f"{url}/clients/bulk"
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in valid_client_data],
    ) as response:
        assert response.status == CREATED
        result = [ClientModel(**each) for each in await response.json()]
        assert result == valid_client_data


@pytest.mark.parametrize(
    ("invalid_params"),
    INVALID_CASES,
)
async def test_bulk_create_invalid(
    http_session: ClientSession,
    url: str,
    valid_client_data: list[ClientModel],
    invalid_params: dict[str, int],
) -> None:
    endpoint = f"{url}/clients/bulk"
    client = valid_client_data[0]
    client = client.model_copy(update=invalid_params)

    async with http_session.post(
        endpoint,
        json=[client.model_dump(mode="json")],
    ) as response:
        assert response.status == UNPROCESSABLE_ENTITY


async def test_bulk_update(
    http_session: ClientSession,
    url: str,
    valid_client_data: list[ClientModel],
) -> None:
    endpoint = f"{url}/clients/bulk"
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in valid_client_data],
    ) as response:
        assert response.status == CREATED
        await response.json()

    updated_data = [client.model_copy(update={"age": client.age + 1}) for client in valid_client_data]
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in updated_data],
    ) as response:
        assert response.status == CREATED
        result = [ClientModel(**each) for each in await response.json()]
        assert result == updated_data


@pytest.fixture
def duplicate_id_data(
    valid_client_data: list[ClientModel],
) -> list[ClientModel]:
    return [valid_client_data[0]] * 2


async def test_duplicate_ids(
    http_session: ClientSession,
    url: str,
    duplicate_id_data: list[ClientModel],
) -> None:
    endpoint = f"{url}/clients/bulk"
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in duplicate_id_data],
    ) as response:
        assert response.status == CREATED
        result = [ClientModel(**each) for each in await response.json()]
        assert len(result) == 1
        assert result[0] == duplicate_id_data[-1]
