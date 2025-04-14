from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import click_campaign, create_unique_client, delete_campaign, show_campaign, update_campaign
from tests.e2e.models import CampaignModel, StatsModel
from tests.e2e.status import NOT_FOUND, OK


async def test_empty(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
    zero_stat: StatsModel,
) -> None:
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}"

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = StatsModel(**(await r.json()))
        assert result == zero_stat


async def test_deleted(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
) -> None:
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}"
    await delete_campaign(
        http_session,
        url,
        str(created_campaign.advertiser_id),
        str(created_campaign.campaign_id),
    )

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND


async def test_not_found(
    http_session: ClientSession,
    url: str,
) -> None:
    endpoint = f"{url}/stats/campaigns/{uuid4()}"

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND


@pytest.mark.parametrize(
    ("count_clicks", "count_impressions"),
    [
        (1, 1),
        (1, 10),
        (4, 5),
        (5, 8),
        (0, 10),
    ],
)
async def test_stats(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
    count_clicks: int,
    count_impressions: int,
) -> None:
    assert count_clicks <= count_impressions
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}"

    clicked = 0
    for _ in range(count_impressions):
        client = await create_unique_client(http_session, url)
        await show_campaign(http_session, url, client_id=client.client_id)

        if clicked < count_clicks:
            await click_campaign(http_session, url, client.client_id, created_campaign.campaign_id)
            clicked += 1

    expected_stat = StatsModel(
        impressions_count=count_impressions,
        clicks_count=count_clicks,
        conversion=count_clicks / count_impressions * 100,
        spent_impressions=count_impressions * created_campaign.cost_per_impression,
        spent_clicks=count_clicks * created_campaign.cost_per_click,
        spent_total=(count_impressions * created_campaign.cost_per_impression)
        + (count_clicks * created_campaign.cost_per_click),
    )

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = StatsModel(**(await r.json()))
        assert result == expected_stat


async def test_update_costs(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
) -> None:
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}"
    spent_impressions = 0.0
    spent_clicks = 0.0
    spent_total = 0.0

    client = await create_unique_client(http_session, url)

    await show_campaign(http_session, url, client_id=client.client_id)
    spent_impressions += created_campaign.cost_per_impression

    await click_campaign(http_session, url, client.client_id, created_campaign.campaign_id)
    spent_clicks += created_campaign.cost_per_click

    created_campaign = await update_campaign(
        http_session,
        url,
        created_campaign,
        update={
            "cost_per_impression": created_campaign.cost_per_impression + 5,
            "cost_per_click": created_campaign.cost_per_click + 5,
        },
    )

    client_o = await create_unique_client(http_session, url)
    await show_campaign(http_session, url, client_id=client_o.client_id)
    spent_impressions += created_campaign.cost_per_impression

    await click_campaign(http_session, url, client_o.client_id, created_campaign.campaign_id)
    spent_clicks += created_campaign.cost_per_click

    spent_total = spent_clicks + spent_impressions
    expected_stat = StatsModel(
        impressions_count=2,
        clicks_count=2,
        conversion=2 / 2 * 100,
        spent_impressions=spent_impressions,
        spent_clicks=spent_clicks,
        spent_total=spent_total,
    )

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = StatsModel(**(await r.json()))
        assert result == expected_stat
