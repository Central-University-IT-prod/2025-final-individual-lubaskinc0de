from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.models import AdvertiserModel, ClientModel, RelevanceModel
from tests.e2e.status import NOT_FOUND, OK, UNPROCESSABLE_ENTITY


@pytest.fixture
def valid_relevance_entry(
    created_clients: list[ClientModel],
    created_advertisers: list[AdvertiserModel],
) -> RelevanceModel:
    return RelevanceModel(
        client_id=created_clients[0].client_id,
        advertiser_id=created_advertisers[0].advertiser_id,
        score=5,
    )


async def test_create(
    http_session: ClientSession,
    url: str,
    valid_relevance_entry: RelevanceModel,
) -> None:
    endpoint = f"{url}/ml-scores"
    async with http_session.post(
        endpoint,
        json=valid_relevance_entry.model_dump(mode="json"),
    ) as response:
        assert response.status == OK


async def test_create_invalid(
    http_session: ClientSession,
    url: str,
    valid_relevance_entry: RelevanceModel,
) -> None:
    endpoint = f"{url}/ml-scores"
    valid_relevance_entry = valid_relevance_entry.model_copy(
        update={"score": -1},
    )
    async with http_session.post(
        endpoint,
        json=valid_relevance_entry.model_dump(mode="json"),
    ) as response:
        assert response.status == UNPROCESSABLE_ENTITY


async def test_update(
    http_session: ClientSession,
    url: str,
    valid_relevance_entry: RelevanceModel,
) -> None:
    endpoint = f"{url}/ml-scores"
    async with http_session.post(
        endpoint,
        json=valid_relevance_entry.model_dump(mode="json"),
    ) as response:
        assert response.status == OK

    updated_data = valid_relevance_entry.model_copy(update={"score": 8})
    async with http_session.post(
        endpoint,
        json=updated_data.model_dump(mode="json"),
    ) as response:
        assert response.status == OK


async def test_create_with_nonexistent_client_id(
    http_session: ClientSession,
    url: str,
    valid_relevance_entry: RelevanceModel,
) -> None:
    endpoint = f"{url}/ml-scores"
    valid_relevance_entry.client_id = uuid4()

    async with http_session.post(
        endpoint,
        json=valid_relevance_entry.model_dump(mode="json"),
    ) as response:
        assert response.status == NOT_FOUND


async def test_create_with_nonexistent_advertiser_id(
    http_session: ClientSession,
    url: str,
    valid_relevance_entry: RelevanceModel,
) -> None:
    endpoint = f"{url}/ml-scores"
    valid_relevance_entry.advertiser_id = uuid4()

    async with http_session.post(
        endpoint,
        json=valid_relevance_entry.model_dump(mode="json"),
    ) as response:
        assert response.status == NOT_FOUND
