from uuid import uuid4

from aiohttp import ClientSession

from tests.e2e.models import CampaignModel
from tests.e2e.status import FORBIDDEN, NO_CONTENT, NOT_FOUND


async def test_delete(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = created_campaigns[0].advertiser_id
    campaign_id = created_campaigns[0].campaign_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.delete(endpoint) as response:
        assert response.status == NO_CONTENT

    async with http_session.delete(endpoint) as response:
        assert response.status == NOT_FOUND


async def test_not_exists_advertiser(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = uuid4()
    campaign_id = created_campaigns[0].campaign_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.delete(endpoint) as response:
        assert response.status == NOT_FOUND


async def test_not_exists_campaign(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = created_campaigns[0].advertiser_id
    campaign_id = uuid4()
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.delete(endpoint) as response:
        assert response.status == NOT_FOUND


async def test_access_denied(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = created_campaigns[1].advertiser_id
    campaign_id = created_campaigns[0].campaign_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.delete(endpoint) as response:
        assert response.status == FORBIDDEN
