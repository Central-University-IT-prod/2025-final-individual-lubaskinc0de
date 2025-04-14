from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import (
    click_campaign,
    create_campaign,
    create_unique_client,
    delete_campaign,
    show_campaign,
)
from tests.e2e.models import AdvertiserModel, CampaignCreateModel, DailyStatsModel
from tests.e2e.status import NOT_FOUND, OK


async def test_empty(
    http_session: ClientSession,
    url: str,
    unique_advertiser: AdvertiserModel,
) -> None:
    endpoint = f"{url}/stats/advertisers/{unique_advertiser.advertiser_id}/campaigns/daily"

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        assert await r.json() == []


async def test_not_found(
    http_session: ClientSession,
    url: str,
) -> None:
    endpoint = f"{url}/stats/advertisers/{uuid4()}/campaigns/daily"

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND


@pytest.mark.parametrize(
    ("days"),
    [
        [
            {
                "day": 0,
                "campaigns": [
                    {
                        "clicks_count": 1,
                        "impressions_count": 2,
                    },
                    {
                        "clicks_count": 1,
                        "impressions_count": 1,
                    },
                ],
            },
            {
                "day": 1,
                "campaigns": [
                    {
                        "clicks_count": 0,
                        "impressions_count": 3,
                    },
                ],
            },
            {
                "day": 2,
                "campaigns": [
                    {
                        "clicks_count": 3,
                        "impressions_count": 7,
                    },
                    {
                        "clicks_count": 1,
                        "impressions_count": 1,
                    },
                ],
            },
            {
                "day": 3,
                "campaigns": [
                    {
                        "clicks_count": 3,
                        "impressions_count": 9,
                    },
                    {
                        "clicks_count": 0,
                        "impressions_count": 5,
                    },
                    {
                        "clicks_count": 8,
                        "impressions_count": 10,
                    },
                    {
                        "clicks_count": 1,
                        "impressions_count": 8,
                    },
                ],
            },
        ],
    ],
)
async def test_stats(
    http_session: ClientSession,
    url: str,
    unique_advertiser: AdvertiserModel,
    campaign_valid_data: CampaignCreateModel,
    days: list[dict[str, int | list[dict[str, int]]]],
) -> None:
    endpoint = f"{url}/stats/advertisers/{unique_advertiser.advertiser_id}/campaigns/daily"
    stats: list[DailyStatsModel] = []
    endpoint_day = f"{url}/time/advance"

    for each in days:
        day_num: int = each["day"]  # type: ignore
        await http_session.post(endpoint_day, json={"current_date": day_num})
        campaigns: list[dict[str, int]] = each["campaigns"]  # type: ignore
        day_stat = DailyStatsModel(
            impressions_count=0,
            clicks_count=0,
            conversion=0.0,
            spent_impressions=0.0,
            spent_clicks=0.0,
            spent_total=0.0,
            date=day_num,
        )

        for campaign_entry in campaigns:
            clicks_count = campaign_entry["clicks_count"]
            impressions_count = campaign_entry["impressions_count"]
            clicked = 0

            data = campaign_valid_data.model_copy(update={"start_date": day_num})
            campaign = await create_campaign(
                http_session,
                url,
                str(unique_advertiser.advertiser_id),
                data,
            )
            for _ in range(impressions_count):
                client = await create_unique_client(http_session, url)
                await show_campaign(http_session, url, client.client_id)
                day_stat.impressions_count += 1

                if clicked < clicks_count:
                    await click_campaign(http_session, url, client.client_id, campaign.campaign_id)
                    clicked += 1
                    day_stat.clicks_count += 1
            await delete_campaign(http_session, url, str(unique_advertiser.advertiser_id), str(campaign.campaign_id))

        day_stat.conversion = round(
            day_stat.clicks_count / day_stat.impressions_count * 100 if day_stat.impressions_count != 0 else 0.0,
            2,
        )
        day_stat.spent_clicks = day_stat.clicks_count * campaign.cost_per_click
        day_stat.spent_impressions = day_stat.impressions_count * campaign.cost_per_impression
        day_stat.spent_total = day_stat.spent_clicks + day_stat.spent_impressions
        stats.append(day_stat)

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = [
            DailyStatsModel(**each).model_copy(update={"conversion": round(each["conversion"], 2)})
            for each in await r.json()
        ]
        assert result == stats
