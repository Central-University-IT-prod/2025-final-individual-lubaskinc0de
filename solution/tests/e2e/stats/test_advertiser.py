from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import (
    click_campaign,
    create_campaign,
    create_unique_client,
    delete_campaign,
    show_campaign,
    update_campaign,
)
from tests.e2e.models import AdvertiserModel, CampaignCreateModel, StatsModel
from tests.e2e.status import NOT_FOUND, OK


async def test_empty(
    http_session: ClientSession,
    url: str,
    zero_stat: StatsModel,
    unique_advertiser: AdvertiserModel,
) -> None:
    endpoint = f"{url}/stats/advertisers/{unique_advertiser.advertiser_id}/campaigns"

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = StatsModel(**(await r.json()))
        assert result == zero_stat


async def test_not_found(
    http_session: ClientSession,
    url: str,
) -> None:
    endpoint = f"{url}/stats/advertisers/{uuid4()}/campaigns"

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND


@pytest.mark.parametrize(
    ("campaigns_count", "impressions_count", "clicks_count"),
    [
        (1, 1, 1),
        (10, 2, 2),
        (10, 2, 1),
        (10, 5, 3),
    ],
)
async def test_stats(
    http_session: ClientSession,
    url: str,
    campaigns_count: int,
    impressions_count: int,
    clicks_count: int,
    unique_advertiser: AdvertiserModel,
    campaign_valid_data: CampaignCreateModel,
) -> None:
    endpoint = f"{url}/stats/advertisers/{unique_advertiser.advertiser_id}/campaigns"
    assert clicks_count <= impressions_count

    spent_impressions = 0.0
    spent_clicks = 0.0

    for _ in range(campaigns_count):
        campaign = await create_campaign(
            http_session,
            url,
            str(unique_advertiser.advertiser_id),
            campaign_valid_data,
        )
        clicked = 0

        for _ in range(impressions_count):
            client = await create_unique_client(http_session, url)
            await show_campaign(http_session, url, client_id=client.client_id)
            spent_impressions += campaign.cost_per_impression

            if clicked < clicks_count:
                await click_campaign(
                    http_session,
                    url,
                    client_id=client.client_id,
                    campaign_id=campaign.campaign_id,
                )
                clicked += 1
                spent_clicks += campaign.cost_per_click
        await delete_campaign(
            http_session,
            url,
            str(campaign.advertiser_id),
            str(campaign.campaign_id),
        )

    total_impressions = impressions_count * campaigns_count
    total_clicks = clicks_count * campaigns_count
    expected_stat = StatsModel(
        impressions_count=total_impressions,
        clicks_count=total_clicks,
        conversion=total_clicks / total_impressions * 100,
        spent_impressions=spent_impressions,
        spent_clicks=spent_clicks,
        spent_total=spent_impressions + spent_clicks,
    )
    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = StatsModel(**(await r.json()))
        assert result == expected_stat


async def test_stats_update_cost(
    http_session: ClientSession,
    url: str,
    unique_advertiser: AdvertiserModel,
    campaign_valid_data: CampaignCreateModel,
) -> None:
    endpoint = f"{url}/stats/advertisers/{unique_advertiser.advertiser_id}/campaigns"

    spent_impressions = 0.0
    spent_clicks = 0.0

    campaign = await create_campaign(
        http_session,
        url,
        str(unique_advertiser.advertiser_id),
        campaign_valid_data,
    )
    client = await create_unique_client(http_session, url)

    await show_campaign(http_session, url, client_id=client.client_id)
    spent_impressions += campaign.cost_per_impression

    await click_campaign(
        http_session,
        url,
        client_id=client.client_id,
        campaign_id=campaign.campaign_id,
    )
    spent_clicks += campaign.cost_per_click

    campaign = await update_campaign(
        http_session,
        url,
        campaign,
        update={
            "cost_per_impression": campaign.cost_per_impression + 5,
            "cost_per_click": campaign.cost_per_click + 5,
        },
    )

    client_o = await create_unique_client(http_session, url)

    await show_campaign(http_session, url, client_id=client_o.client_id)
    spent_impressions += campaign.cost_per_impression

    await click_campaign(
        http_session,
        url,
        client_id=client_o.client_id,
        campaign_id=campaign.campaign_id,
    )
    spent_clicks += campaign.cost_per_click

    total_impressions = 2
    total_clicks = 2
    expected_stat = StatsModel(
        impressions_count=total_impressions,
        clicks_count=total_clicks,
        conversion=total_clicks / total_impressions * 100,
        spent_impressions=spent_impressions,
        spent_clicks=spent_clicks,
        spent_total=spent_impressions + spent_clicks,
    )
    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = StatsModel(**(await r.json()))
        assert result == expected_stat
