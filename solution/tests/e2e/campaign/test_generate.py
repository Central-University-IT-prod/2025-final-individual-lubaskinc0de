from http.client import NOT_FOUND
from uuid import uuid4

from aiohttp import ClientSession

from crudik.application.data_model.campaign import CampaignData
from tests.e2e.status import OK


async def test_generate(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignData,
) -> None:
    created_campaign.ad_title = "Продаем бананы"
    advertiser_id = created_campaign.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/generate?ad_title={created_campaign.ad_title}"

    async with http_session.get(
        endpoint,
    ) as response:
        assert response.status == OK
        json = await response.json()
        assert "ad_text" in json
        assert len(json["ad_text"]) > 10  # noqa: PLR2004


async def test_not_exists_advertiser(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignData,
) -> None:
    advertiser_id = uuid4()
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/generate?ad_title={created_campaign.ad_title}"

    async with http_session.get(
        endpoint,
    ) as response:
        assert response.status == NOT_FOUND
