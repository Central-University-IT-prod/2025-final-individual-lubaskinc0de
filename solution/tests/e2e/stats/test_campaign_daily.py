from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import click_campaign, create_unique_client, delete_campaign, show_campaign
from tests.e2e.models import CampaignModel, ClientModel, DailyStatsModel
from tests.e2e.status import NOT_FOUND, OK


async def test_empty(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
) -> None:
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}/daily"

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        assert (await r.json()) == []


async def test_deleted(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
) -> None:
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}/daily"
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
    endpoint = f"{url}/stats/campaigns/{uuid4()}/daily"

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND


@pytest.mark.parametrize(
    ("days"),
    [
        [
            {
                "day": 0,
                "clicks_count": 0,
                "impressions_count": 1,
            },
            {
                "day": 1,
                "clicks_count": 0,
                "impressions_count": 1,
            },
            {
                "day": 2,
                "clicks_count": 4,
                "impressions_count": 5,
            },
            {
                "day": 3,
                "clicks_count": 5,
                "impressions_count": 5,
            },
            {
                "day": 4,
                "clicks_count": 1,
                "impressions_count": 5,
            },
        ],
    ],
)
async def test_daily_stats(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
    days: list[dict[str, int]],
) -> None:
    stats: list[DailyStatsModel] = []
    campaign = created_campaign
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}/daily"

    for each in days:
        day_num = each["day"]
        clicks_count = each["clicks_count"]
        impressions_count = each["impressions_count"]
        clicked = 0
        endpoint_day = f"{url}/time/advance"
        await http_session.post(endpoint_day, json={"current_date": day_num})

        daily_stat = DailyStatsModel(
            impressions_count=impressions_count,
            clicks_count=clicks_count,
            conversion=clicks_count / impressions_count * 100 if impressions_count != 0 else 0.0,
            spent_impressions=0.0,
            spent_clicks=0.0,
            spent_total=0.0,
            date=day_num,
        )
        for _ in range(impressions_count):
            client = await create_unique_client(http_session, url)
            await show_campaign(http_session, url, client.client_id)
            daily_stat.spent_impressions += campaign.cost_per_impression

            if clicked < clicks_count:
                await click_campaign(http_session, url, client.client_id, campaign.campaign_id)
                daily_stat.spent_clicks += campaign.cost_per_click
                clicked += 1
        daily_stat.spent_total = daily_stat.spent_impressions + daily_stat.spent_clicks
        stats.append(daily_stat)

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = [DailyStatsModel(**each) for each in await r.json()]
        assert result == stats


async def test_daily_stats_sequential(
    http_session: ClientSession,
    url: str,
    created_campaign: CampaignModel,
    unique_client: ClientModel,
) -> None:
    stats: list[DailyStatsModel] = []
    endpoint_day = f"{url}/time/advance"
    endpoint = f"{url}/stats/campaigns/{created_campaign.campaign_id}/daily"

    await show_campaign(http_session, url, unique_client.client_id)
    stats.append(
        DailyStatsModel(
            impressions_count=1,
            clicks_count=0,
            conversion=0.0,
            spent_impressions=created_campaign.cost_per_impression,
            spent_clicks=0.0,
            spent_total=created_campaign.cost_per_impression,
            date=0,
        ),
    )

    await http_session.post(endpoint_day, json={"current_date": 1})

    await click_campaign(http_session, url, unique_client.client_id, created_campaign.campaign_id)
    stats.append(
        DailyStatsModel(
            impressions_count=0,
            clicks_count=1,
            conversion=0.0,
            spent_impressions=0.0,
            spent_clicks=created_campaign.cost_per_click,
            spent_total=created_campaign.cost_per_click,
            date=1,
        ),
    )

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = [DailyStatsModel(**each) for each in await r.json()]
        assert result == stats
