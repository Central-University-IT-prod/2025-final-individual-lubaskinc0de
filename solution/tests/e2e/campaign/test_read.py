from pathlib import Path
from uuid import uuid4

from aiohttp import ClientSession

from tests.e2e.conftest import create_campaign, create_campaign_with_image, delete_campaign
from tests.e2e.models import AdvertiserModel, CampaignCreateModel, CampaignModel
from tests.e2e.status import FORBIDDEN, NOT_FOUND, OK


async def test_read(
    http_session: ClientSession,
    url: str,
    unique_advertiser: AdvertiserModel,
    campaign_valid_data: CampaignCreateModel,
    image: tuple[Path, str],
) -> None:
    campaign = await create_campaign_with_image(
        http_session,
        url,
        str(unique_advertiser.advertiser_id),
        campaign_valid_data,
        *image,
    )
    endpoint = f"{url}/advertisers/{unique_advertiser.advertiser_id}/campaigns/{campaign.campaign_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == OK
        json = await response.json()
        assert CampaignModel(**json) == campaign


async def test_read_not_exists_advertiser(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = uuid4()
    campaign_id = created_campaigns[0].campaign_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == NOT_FOUND


async def test_read_not_exists_campaign(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = created_campaigns[0].advertiser_id
    campaign_id = uuid4()
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == NOT_FOUND


async def test_read_access_denied(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = created_campaigns[1].advertiser_id
    campaign_id = created_campaigns[0].campaign_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == FORBIDDEN


async def test_read_nulls(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    created_advertisers: list[AdvertiserModel],
) -> None:
    if campaign_valid_data.targeting is None:
        raise RuntimeError("Empty targeting in fixture.")

    for field in campaign_valid_data.targeting.model_fields:
        setattr(campaign_valid_data.targeting, field, None)

    advertiser_id = created_advertisers[0].advertiser_id
    campaign = await create_campaign(
        http_session,
        url,
        str(advertiser_id),
        campaign_valid_data,
    )

    campaign_id = campaign.campaign_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"

    async with http_session.get(endpoint) as response:
        assert response.status == OK
        json = await response.json()
        CampaignModel.model_validate(json)

        dumped = campaign.model_dump(mode="json")
        dumped = {k: v for k, v in dumped.items() if v is not None}

        if dumped["targeting"]:
            dumped["targeting"] = {k: v for k, v in dumped["targeting"].items() if v is not None}
        assert json == dumped


async def test_read_deleted(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    advertiser_id = created_campaigns[0].advertiser_id
    campaign_id = created_campaigns[0].campaign_id
    await delete_campaign(http_session, url, str(advertiser_id), str(campaign_id))

    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    async with http_session.get(endpoint) as response:
        assert response.status == NOT_FOUND
