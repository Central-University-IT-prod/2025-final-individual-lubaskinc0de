from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import create_campaign, delete_campaign
from tests.e2e.models import (
    AdvertiserModel,
    CampaignCreateModel,
    CampaignModel,
    CampaignUpdateModel,
    TargetingGenderModel,
)
from tests.e2e.status import FORBIDDEN, NO_CONTENT, NOT_FOUND, OK, UNPROCESSABLE_ENTITY

CURRENT_DATE = 3

INVALID_CASES = [
    {"impressions_limit": -100},
    {"clicks_limit": -50},
    {"cost_per_impression": -0.5},
    {"cost_per_click": -2.0},
    {"ad_title": None},
    {"start_date": CURRENT_DATE - 1},
    {"end_date": CURRENT_DATE - 1},
    {"start_date": CURRENT_DATE + 2, "end_date": CURRENT_DATE + 1},
    {"targeting": {"age_from": -1}},
    {"targeting": {"age_from": 101}},
    {"targeting": {"age_to": -1}},
    {"targeting": {"age_to": 101}},
    {
        "ad_title": "хуй",
    },
    {
        "ad_text": "говно",
    },
    {
        "ad_title": "нормальное",
        "ad_text": "хуйня ебанная",
    },
    {
        "ad_title": "дро$ила",
    },
    {
        "ad_title": "муд@к",
    },
    {
        "ad_title": "N@hU1 id1",
    },
    {
        "ad_title": "fuck you",
    },
    {
        "ad_title": "motherfucker",
    },
    {
        "ad_title": "b1tch",
    },
]


@pytest.mark.parametrize(
    (
        "current_day",
        "impressions_add",
        "clicks_add",
        "start_add",
        "end_add",
        "start_date",
    ),
    [
        (0, 0, 0, 0, 0, 0),
        (1, 100, 100, 2, 3, 2),
    ],
)
async def test_update(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    unique_advertiser: AdvertiserModel,
    current_day: int,
    impressions_add: int,
    clicks_add: int,
    start_add: int,
    end_add: int,
    start_date: int,
) -> None:
    create_data = campaign_valid_data.model_copy(
        update={"start_date": start_date},
    )
    src = await create_campaign(
        http_session,
        url,
        str(unique_advertiser.advertiser_id),
        create_data,
    )

    time_endpoint = f"{url}/time/advance"
    await http_session.post(time_endpoint, json={"current_date": current_day})

    advertiser_id = src.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{src.campaign_id}"
    updated = src.model_copy(
        update={
            "cost_per_click": src.cost_per_click + 1,
            "cost_per_impression": src.cost_per_impression + 1000,
            "ad_title": src.ad_title + "aaa",
            "ad_text": src.ad_text + "bbb",
            "impressions_limit": src.impressions_limit + impressions_add,
            "clicks_limit": src.clicks_limit + clicks_add,
            "start_date": src.start_date + start_add,
            "end_date": src.end_date + end_add,
            "targeting": {
                "age_from": 50,
                "age_to": 60,
                "location": "Питер",
                "gender": TargetingGenderModel.ALL,
            },
        },
    )

    payload = CampaignUpdateModel(
        cost_per_click=updated.cost_per_click,
        cost_per_impression=updated.cost_per_impression,
        ad_title=updated.ad_title,
        ad_text=updated.ad_text,
        targeting=updated.targeting,
        impressions_limit=updated.impressions_limit,
        clicks_limit=updated.clicks_limit,
        start_date=updated.start_date,
        end_date=updated.end_date,
    )

    async with http_session.put(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        assert response.status == OK
        data = CampaignModel(**(await response.json()))
        assert data.model_dump() == updated.model_dump()


@pytest.mark.parametrize(
    ("invalid_params"),
    INVALID_CASES,
)
async def test_update_invalid(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    invalid_params: dict[str, int | None],
    unique_advertiser: AdvertiserModel,
) -> None:
    time_endpoint = f"{url}/time/advance"
    await http_session.post(time_endpoint, json={"current_date": CURRENT_DATE})
    campaign_valid_data.start_date = CURRENT_DATE

    toggle_endpoint = f"{url}/advertisers/toggle/swears"
    async with http_session.put(toggle_endpoint, json={"check_enabled": 1}) as r:
        assert r.status == NO_CONTENT

    src = await create_campaign(http_session, url, str(unique_advertiser.advertiser_id), campaign_valid_data)

    advertiser_id = src.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{src.campaign_id}"
    updated = src.model_copy(
        update={
            "start_date": CURRENT_DATE,
            **invalid_params,
        },
    )

    payload = CampaignUpdateModel(
        cost_per_click=updated.cost_per_click,
        cost_per_impression=updated.cost_per_impression,
        ad_title=updated.ad_title,
        ad_text=updated.ad_text,
        targeting=updated.targeting,
        impressions_limit=updated.impressions_limit,
        clicks_limit=updated.clicks_limit,
        start_date=updated.start_date,
        end_date=updated.end_date,
    )

    async with http_session.put(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        assert response.status == UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    ("invalid_params"),
    [
        {"impressions_limit": 3},
        {"clicks_limit": 3},
        {"start_date": 1},
        {"end_date": 0},
    ],
)
async def test_edit_after_start(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
    invalid_params: dict[str, int | None],
) -> None:
    src = created_campaigns[0]

    advertiser_id = src.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{src.campaign_id}"
    updated = src.model_copy(
        update={
            **invalid_params,
        },
    )

    payload = CampaignUpdateModel(
        cost_per_click=updated.cost_per_click,
        cost_per_impression=updated.cost_per_impression,
        ad_title=updated.ad_title,
        ad_text=updated.ad_text,
        targeting=updated.targeting,
        impressions_limit=updated.impressions_limit,
        clicks_limit=updated.clicks_limit,
        start_date=updated.start_date,
        end_date=updated.end_date,
    )

    async with http_session.put(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        error_data = await response.json()
        assert response.status == UNPROCESSABLE_ENTITY
        assert error_data["code"] == "CANNOT_CHANGE_CAMPAIGN_AFTER_START"


@pytest.mark.parametrize(
    ("invalid_params", "current_day"),
    [
        ({"start_date": 1}, 2),
        ({"end_date": 0}, 1),
        ({"start_date": 1, "end_date": 0}, 0),
    ],
)
async def test_dates_in_past(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    unique_advertiser: AdvertiserModel,
    invalid_params: dict[str, int | None],
    current_day: int,
) -> None:
    create_data = campaign_valid_data.model_copy(
        update={"start_date": current_day + 1},
    )
    src = await create_campaign(
        http_session,
        url,
        str(unique_advertiser.advertiser_id),
        create_data,
    )

    time_endpoint = f"{url}/time/advance"
    await http_session.post(time_endpoint, json={"current_date": current_day})

    advertiser_id = src.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{src.campaign_id}"
    updated = src.model_copy(
        update={
            **invalid_params,
        },
    )

    payload = CampaignUpdateModel(
        cost_per_click=updated.cost_per_click,
        cost_per_impression=updated.cost_per_impression,
        ad_title=updated.ad_title,
        ad_text=updated.ad_text,
        targeting=updated.targeting,
        impressions_limit=updated.impressions_limit,
        clicks_limit=updated.clicks_limit,
        start_date=updated.start_date,
        end_date=updated.end_date,
    )

    async with http_session.put(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        error_data = await response.json()
        assert response.status == UNPROCESSABLE_ENTITY
        assert error_data["code"] == "CAMPAIGN_CANNOT_BE_IN_PAST"


async def test_update_not_exists_advertiser(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    src = created_campaigns[0]
    advertiser_id = uuid4()
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{src.campaign_id}"

    async with http_session.put(
        endpoint,
        json=src.model_dump(mode="json"),
    ) as response:
        assert response.status == NOT_FOUND


async def test_update_not_exists_campaign(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    src = created_campaigns[0]
    endpoint = f"{url}/advertisers/{src.advertiser_id}/campaigns/{uuid4()}"

    async with http_session.put(
        endpoint,
        json=src.model_dump(mode="json"),
    ) as response:
        assert response.status == NOT_FOUND


async def test_update_access_denied(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
    unique_advertiser: AdvertiserModel,
) -> None:
    src = created_campaigns[0]
    endpoint = f"{url}/advertisers/{unique_advertiser.advertiser_id}/campaigns/{src.campaign_id}"

    async with http_session.put(
        endpoint,
        json=src.model_dump(mode="json"),
    ) as response:
        assert response.status == FORBIDDEN


async def test_update_deleted(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
) -> None:
    src = created_campaigns[0]
    advertiser_id = created_campaigns[0].advertiser_id

    await delete_campaign(http_session, url, str(advertiser_id), str(src.campaign_id))

    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{src.campaign_id}"
    async with http_session.put(
        endpoint,
        json=src.model_dump(mode="json"),
    ) as response:
        assert response.status == NOT_FOUND
