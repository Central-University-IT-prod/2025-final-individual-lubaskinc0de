from uuid import uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.models import (
    AdvertiserModel,
    CampaignCreateModel,
    CampaignModel,
    TargetingGenderModel,
    TargetingModel,
)
from tests.e2e.status import CREATED, NO_CONTENT, NOT_FOUND, UNPROCESSABLE_ENTITY

CURRENT_DATE = 3
FEMALE = TargetingGenderModel.FEMALE
MALE = TargetingGenderModel.MALE
ALL = TargetingGenderModel.ALL

INVALID_CASES = [
    {"impressions_limit": -100},
    {"clicks_limit": -50},
    {"clicks_limit": 2, "impressions_limit": 1},
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
]


@pytest.fixture
def base_payload() -> CampaignCreateModel:
    return CampaignCreateModel(
        impressions_limit=1000,
        clicks_limit=1000,
        cost_per_impression=0.5,
        cost_per_click=2.0,
        ad_title="Test Campaign",
        ad_text="Test campaign description",
        start_date=0,
        end_date=7,
        targeting=TargetingModel(
            gender=None,
            age_from=None,
            age_to=None,
            location=None,
        ),
    )


@pytest.mark.parametrize(
    "targeting",
    [
        TargetingModel(age_from=None, age_to=None, location=None, gender=None),
        TargetingModel(
            age_from=None,
            age_to=30,
            location="London",
            gender=FEMALE,
        ),
        TargetingModel(age_from=18, age_to=None, location="Paris", gender=MALE),
        TargetingModel(age_from=25, age_to=40, location=None, gender=ALL),
        TargetingModel(age_from=30, age_to=50, location="Berlin", gender=None),
        TargetingModel(age_from=18, age_to=35, location="NY", gender=MALE),
        TargetingModel(
            gender=None,
            age_from=None,
            age_to=None,
            location=None,
        ),
    ],
)
async def test_create(
    http_session: ClientSession,
    url: str,
    created_advertisers: list[AdvertiserModel],
    targeting: TargetingModel,
    base_payload: CampaignCreateModel,
) -> None:
    advertiser_id = created_advertisers[0].advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

    payload = base_payload.model_copy(update={"targeting": targeting})

    async with http_session.post(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        assert response.status == CREATED
        result = CampaignModel(**await response.json())

        expected_campaign = CampaignModel(
            **payload.model_dump(),
            advertiser_id=advertiser_id,
            campaign_id=result.campaign_id,
        )

        assert result == expected_campaign


@pytest.mark.parametrize(
    "invalid_params",
    INVALID_CASES,
)
async def test_create_invalid(
    http_session: ClientSession,
    url: str,
    created_advertisers: list[AdvertiserModel],
    invalid_params: dict[str, int | None],
    base_payload: CampaignCreateModel,
) -> None:
    advertiser_id = created_advertisers[0].advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"
    time_endpoint = f"{url}/time/advance"
    await http_session.post(time_endpoint, json={"current_date": CURRENT_DATE})

    payload = base_payload.model_copy(update=invalid_params)

    async with http_session.post(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        assert response.status == UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "invalid_params",
    [
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
    ],
)
async def test_create_swears(
    http_session: ClientSession,
    url: str,
    created_advertisers: list[AdvertiserModel],
    invalid_params: dict[str, int | None],
    base_payload: CampaignCreateModel,
) -> None:
    advertiser_id = created_advertisers[0].advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

    toggle_endpoint = f"{url}/advertisers/toggle/swears"
    async with http_session.put(toggle_endpoint, json={"check_enabled": 1}) as r:
        assert r.status == NO_CONTENT

    payload = base_payload.model_copy(update=invalid_params)

    async with http_session.post(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        assert response.status == UNPROCESSABLE_ENTITY
        result = await response.json()
        code = result["code"]
        assert code == "CAMPAIGN_CONTAINS_SWEARS"


async def test_create_not_exists_advertiser(
    http_session: ClientSession,
    url: str,
    base_payload: CampaignCreateModel,
) -> None:
    advertiser_id = uuid4()
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

    async with http_session.post(
        endpoint,
        json=base_payload.model_dump(mode="json"),
    ) as response:
        assert response.status == NOT_FOUND
