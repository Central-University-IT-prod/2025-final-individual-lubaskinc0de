from uuid import uuid4

from aiohttp import ClientSession

from tests.e2e.models import AdvertiserModel
from tests.e2e.status import NOT_FOUND, OK


async def test_read_existing(
    http_session: ClientSession,
    url: str,
    created_advertisers: list[AdvertiserModel],
) -> None:
    advertiser = created_advertisers[0]
    advertiser_id = advertiser.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == OK
        data = await response.json()
        assert AdvertiserModel(**data) == advertiser


async def test_read_nonexistent(
    http_session: ClientSession,
    url: str,
) -> None:
    non_existent_id = str(uuid4())
    endpoint = f"{url}/advertisers/{non_existent_id}"
    async with http_session.get(endpoint) as response:
        assert response.status == NOT_FOUND
