from typing import NotRequired, TypedDict
from uuid import UUID, uuid4

import pytest
from aiohttp import ClientSession

from tests.e2e.conftest import (
    campaign_to_ad,
    create_campaign,
    create_unique_advertiser,
    create_unique_client,
    set_relevance,
)
from tests.e2e.models import AdModel, CampaignCreateModel, CampaignModel, ClientModel
from tests.e2e.status import NOT_FOUND, OK


class ChoiceCase(TypedDict):
    cost_per_impression: float
    cost_per_click: float
    ml_score: int
    choice: NotRequired[bool]


ad_choice_cases: list[list[ChoiceCase]] = [
    [
        {
            "cost_per_impression": 0.0,
            "cost_per_click": 0.0,
            "ml_score": 2,
        },
        {
            "cost_per_impression": 5.0,
            "cost_per_click": 3.0,
            "ml_score": 1,
            "choice": True,
        },
    ],
    [
        {
            "cost_per_impression": 100,
            "cost_per_click": 10,
            "ml_score": 10,
        },
        {
            "cost_per_impression": 50,
            "cost_per_click": 100,
            "ml_score": 50,
            "choice": True,
        },
    ],
    [
        {
            "cost_per_impression": 1000,
            "cost_per_click": 10,
            "ml_score": 10,
            "choice": True,
        },
        {
            "cost_per_impression": 50,
            "cost_per_click": 100,
            "ml_score": 50,
        },
    ],
    [
        {
            "cost_per_impression": 10_000,
            "cost_per_click": 0,
            "ml_score": 10,
            "choice": True,
        },
        {
            "cost_per_impression": 50,
            "cost_per_click": 100,
            "ml_score": 50,
        },
    ],
    [
        {
            "cost_per_impression": 1000,
            "cost_per_click": 100,
            "ml_score": 10,
            "choice": True,
        },
        {
            "cost_per_impression": 50,
            "cost_per_click": 100,
            "ml_score": 200,
        },
    ],
    [
        {
            "cost_per_impression": 0,
            "cost_per_click": 0,
            "ml_score": 1000,
            "choice": True,
        },
        {
            "cost_per_impression": 0,
            "cost_per_click": 0,
            "ml_score": 50,
        },
    ],
    [
        {
            "cost_per_impression": 0,
            "cost_per_click": 5000,
            "ml_score": 1000,
            "choice": True,
        },
        {
            "cost_per_impression": 50,
            "cost_per_click": 100,
            "ml_score": 1500,
        },
    ],
    [
        {
            "cost_per_impression": 0,
            "cost_per_click": 5000,
            "ml_score": 1000,
            "choice": True,
        },
        {
            "cost_per_impression": 50,
            "cost_per_click": 100,
            "ml_score": 1500,
        },
        {
            "cost_per_impression": 100,
            "cost_per_click": 200,
            "ml_score": 2000,
        },
    ],
    [
        {
            "cost_per_impression": 1000000,
            "cost_per_click": 0,
            "ml_score": 5,
            "choice": True,
        },
        {
            "cost_per_impression": 100,
            "cost_per_click": 200,
            "ml_score": 2000,
        },
    ],
]


async def test_simple(
    created_campaign: CampaignModel,
    unique_client: ClientModel,
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads?client_id={unique_client.client_id}"

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = AdModel(**(await r.json()))
        assert result == campaign_to_ad(created_campaign)


@pytest.mark.parametrize(
    "cases",
    ad_choice_cases,
)
async def test_choice(
    url: str,
    http_session: ClientSession,
    cases: list[ChoiceCase],
    campaign_valid_data: CampaignCreateModel,
) -> None:
    client = await create_unique_client(http_session, url)
    choice: None | UUID = None

    for case in cases:
        advertiser = await create_unique_advertiser(http_session, url)
        score = case["ml_score"]
        is_choice = case.get("choice", False)
        if is_choice:
            case.pop("choice")

        data = campaign_valid_data.model_copy(update=case)
        campaign = await create_campaign(
            http_session,
            url,
            str(advertiser.advertiser_id),
            data,
        )
        await set_relevance(http_session, url, advertiser.advertiser_id, client.client_id, score)

        if is_choice and choice is None:
            choice = campaign.campaign_id

    assert choice is not None
    endpoint = f"{url}/ads?client_id={client.client_id}"

    async with http_session.get(endpoint) as r:
        assert r.status == OK
        result = AdModel(**(await r.json()))
        assert result.ad_id == choice


async def test_client_not_exists(
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads?client_id={uuid4()}"

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND


async def test_no_ad(
    unique_client: ClientModel,
    url: str,
    http_session: ClientSession,
) -> None:
    endpoint = f"{url}/ads?client_id={unique_client.client_id}"

    async with http_session.get(endpoint) as r:
        assert r.status == NOT_FOUND
