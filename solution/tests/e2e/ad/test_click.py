from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import delete_campaign
from tests.e2e.models import CampaignModel, ClientModel
from tests.e2e.status import FORBIDDEN, NO_CONTENT, NOT_FOUND


@pytest.mark.parametrize(
    ("repeats"),
    [
        1,
        3,
        5,
    ],
)
async def test_click(
    shown_campaign: CampaignModel,
    unique_client: ClientModel,
    url: str,
    http_session: ClientSession,
    repeats: int,
) -> None:
    for _ in range(repeats):
        endpoint = f"{url}/ads/{shown_campaign.campaign_id}/click"

        async with http_session.post(
            endpoint,
            json={"client_id": str(unique_client.client_id)},
        ) as response:
            assert response.status == NO_CONTENT


async def test_click_deleted(
    shown_campaign: CampaignModel,
    unique_client: ClientModel,
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads/{shown_campaign.campaign_id}/click"
    await delete_campaign(
        http_session,
        url,
        str(shown_campaign.advertiser_id),
        str(shown_campaign.campaign_id),
    )
    async with http_session.post(
        endpoint,
        json={"client_id": str(unique_client.client_id)},
    ) as response:
        assert response.status == NOT_FOUND


async def test_click_without_impression(
    created_campaigns: list[CampaignModel],
    unique_client: ClientModel,
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads/{created_campaigns[0].campaign_id}/click"

    async with http_session.post(
        endpoint,
        json={"client_id": str(unique_client.client_id)},
    ) as response:
        assert response.status == FORBIDDEN


async def test_click_not_found_client(
    shown_campaign: CampaignModel,
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads/{shown_campaign.campaign_id}/click"

    async with http_session.post(
        endpoint,
        json={"client_id": str(uuid4())},
    ) as response:
        assert response.status == NOT_FOUND


async def test_click_not_found_campaign(
    unique_client: ClientModel,
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads/{uuid4()}/click"

    async with http_session.post(
        endpoint,
        json={"client_id": str(unique_client.client_id)},
    ) as response:
        assert response.status == NOT_FOUND
