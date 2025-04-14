import pytest
from aiohttp import ClientSession

from tests.e2e.models import AdvertiserModel
from tests.e2e.status import CREATED


async def test_bulk_create(
    http_session: ClientSession,
    url: str,
    valid_advertiser_data: list[AdvertiserModel],
) -> None:
    endpoint = f"{url}/advertisers/bulk"
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in valid_advertiser_data],
    ) as response:
        assert response.status == CREATED
        result = [AdvertiserModel(**each) for each in await response.json()]
        assert result == valid_advertiser_data


async def test_bulk_update(
    http_session: ClientSession,
    url: str,
    valid_advertiser_data: list[AdvertiserModel],
) -> None:
    endpoint = f"{url}/advertisers/bulk"
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in valid_advertiser_data],
    ) as response:
        assert response.status == CREATED

    updated_data = [adv.model_copy(update={"name": adv.name + "a"}) for adv in valid_advertiser_data]
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in updated_data],
    ) as response:
        assert response.status == CREATED
        result = [AdvertiserModel(**each) for each in await response.json()]
        assert result == updated_data


@pytest.fixture
def duplicate_id_data(
    valid_advertiser_data: list[AdvertiserModel],
) -> list[AdvertiserModel]:
    return [valid_advertiser_data[0]] * 2


async def test_duplicate_ids(
    http_session: ClientSession,
    url: str,
    duplicate_id_data: list[AdvertiserModel],
) -> None:
    endpoint = f"{url}/advertisers/bulk"
    async with http_session.post(
        endpoint,
        json=[each.model_dump(mode="json") for each in duplicate_id_data],
    ) as response:
        result = [AdvertiserModel(**each) for each in await response.json()]
        assert response.status == CREATED
        assert len(result) == 1
        assert result[0] == duplicate_id_data[-1]
