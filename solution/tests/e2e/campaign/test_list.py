import asyncio
import random
from pathlib import Path

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import create_campaign_with_image, delete_campaign
from tests.e2e.models import AdvertiserModel, CampaignCreateModel, CampaignModel
from tests.e2e.status import OK, UNPROCESSABLE_ENTITY

COUNT_CAMPAIGNS = 10


@pytest.mark.parametrize(
    ("size", "page", "count_campaigns"),
    [
        (None, None, 0),
        (None, None, COUNT_CAMPAIGNS),
        (COUNT_CAMPAIGNS // 2, 1, COUNT_CAMPAIGNS),
        (COUNT_CAMPAIGNS // 2, None, COUNT_CAMPAIGNS),
        (None, 1, COUNT_CAMPAIGNS),
        (1, 0, COUNT_CAMPAIGNS),
        (0, 1, COUNT_CAMPAIGNS),
    ],
)
async def test_list(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    unique_advertiser: AdvertiserModel,
    size: int | None,
    page: int | None,
    count_campaigns: int,
    image: tuple[Path, str],
) -> None:
    advertiser_id = unique_advertiser.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

    requests = [
        create_campaign_with_image(
            http_session,
            url,
            str(advertiser_id),
            campaign_valid_data,
            *image,
        )
        for _ in range(count_campaigns)
    ]
    campaigns_unsorted = await asyncio.gather(*requests)
    campaigns = sorted(
        campaigns_unsorted,
        key=lambda c: (c.ad_title, c.campaign_id),
    )

    if campaigns:
        to_delete = campaigns.pop(random.randint(0, len(campaigns) - 1))  # noqa: S311
        await delete_campaign(http_session, url, str(advertiser_id), str(to_delete.campaign_id))

    limit, offset = None, None
    if size is not None:
        limit = size

    if size is not None and page is not None:
        offset = size * page

    if limit is not None or offset is not None:
        endpoint += "?"

    if offset is not None:
        campaigns = campaigns[offset:]
        endpoint += f"page={page}&"
    if limit is not None:
        campaigns = campaigns[:limit]
        endpoint += f"size={limit}"

    async with http_session.get(endpoint) as response:
        assert response.status == OK
        json = await response.json()
        assert len(json) == len(campaigns)

        results = [CampaignModel(**each) for each in json]
        assert results == campaigns


async def test_list_by_advertiser(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    created_advertisers: list[AdvertiserModel],
    image: tuple[Path, str],
) -> None:
    count_campaigns = COUNT_CAMPAIGNS // 5
    for advertiser in created_advertisers:
        endpoint = f"{url}/advertisers/{advertiser.advertiser_id}/campaigns?page=0&size={count_campaigns}"
        requests = [
            create_campaign_with_image(
                http_session,
                url,
                str(advertiser.advertiser_id),
                campaign_valid_data,
                *image,
            )
            for _ in range(count_campaigns)
        ]
        campaigns_unsorted = await asyncio.gather(*requests)
        campaigns = sorted(
            campaigns_unsorted,
            key=lambda c: (c.ad_title, c.campaign_id),
        )

        async with http_session.get(endpoint) as response:
            assert response.status == OK
            json = await response.json()
            assert len(json) == len(campaigns)

            results = [CampaignModel(**each) for each in json]
            assert results == campaigns


@pytest.mark.parametrize(
    ("size", "page"),
    [
        (-1, 1),
        (1, -1),
    ],
)
async def test_list_invalid(
    http_session: ClientSession,
    url: str,
    unique_advertiser: AdvertiserModel,
    size: int,
    page: int,
) -> None:
    advertiser_id = unique_advertiser.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns?size={size}&page={page}"

    async with http_session.get(endpoint) as response:
        assert response.status == UNPROCESSABLE_ENTITY
