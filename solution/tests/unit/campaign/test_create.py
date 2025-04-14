from typing import Any

import pytest
from pydantic import ValidationError

from crudik.application.campaign.create import CreateCampaign
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.data_model.campaign import CampaignCreateData, CampaignTargeting
from crudik.application.exceptions.campaign import (
    CampaignCannotBeInPastError,
    CampaignContainsSwearsError,
    ClickLimitGreaterThanImpressionsLimitError,
)
from crudik.domain.entity.advertiser import Advertiser


async def test_ok(
    create_campaign: CreateCampaign,
    campaign_gateway: CampaignGateway,
    unique_advertiser: Advertiser,
) -> None:
    created = await create_campaign.execute(
        advertiser_id=unique_advertiser.advertiser_id,
        data=CampaignCreateData(
            impressions_limit=100,
            clicks_limit=100,
            cost_per_impression=100,
            cost_per_click=100,
            ad_title="some",
            ad_text="some",
            start_date=0,
            end_date=100,
            targeting=CampaignTargeting(),
        ),
    )
    assert await campaign_gateway.get_by_id(created.campaign_id) is not None


@pytest.mark.parametrize(
    "invalid_params",
    [
        {"impressions_limit": -100, "raises": ValidationError},
        {"clicks_limit": -50, "raises": ValidationError},
        {"clicks_limit": 2, "impressions_limit": 1, "raises": ClickLimitGreaterThanImpressionsLimitError},
        {"cost_per_impression": -0.5, "raises": ValidationError},
        {"cost_per_click": -2.0, "raises": ValidationError},
        {"start_date": 5, "end_date": 4, "raises": CampaignCannotBeInPastError},
    ],
)
async def test_invalid(
    create_campaign: CreateCampaign,
    unique_advertiser: Advertiser,
    invalid_params: dict[str, Any],
) -> None:
    raises = invalid_params.pop("raises")
    data = CampaignCreateData(
        impressions_limit=100,
        clicks_limit=100,
        cost_per_impression=100,
        cost_per_click=100,
        ad_title="some",
        ad_text="some",
        start_date=0,
        end_date=100,
        targeting=CampaignTargeting(),
    )
    with pytest.raises(raises):
        data = data.model_copy(update=invalid_params)
        data.model_validate(data.model_dump())
        await create_campaign.execute(
            advertiser_id=unique_advertiser.advertiser_id,
            data=data,
        )


@pytest.mark.parametrize(
    ("invalid_params", "current_day"),
    [
        ({"start_date": 0}, 1),
        ({"end_date": 10}, 11),
        ({"start_date": 2, "end_date": 1}, 0),
    ],
)
async def test_invalid_dates(
    create_campaign: CreateCampaign,
    unique_advertiser: Advertiser,
    invalid_params: dict[str, Any],
    day_gateway: DayGateway,
    current_day: int,
) -> None:
    await day_gateway.set_current_day(current_day)
    data = CampaignCreateData(
        impressions_limit=100,
        clicks_limit=100,
        cost_per_impression=100,
        cost_per_click=100,
        ad_title="some",
        ad_text="some",
        start_date=0,
        end_date=100,
        targeting=CampaignTargeting(),
    )
    with pytest.raises(CampaignCannotBeInPastError):
        data = data.model_copy(update=invalid_params)
        await create_campaign.execute(
            advertiser_id=unique_advertiser.advertiser_id,
            data=data,
        )


async def test_swears(
    create_campaign: CreateCampaign,
    unique_advertiser: Advertiser,
    swear_filter: SwearFilter,
) -> None:
    await swear_filter.set_mode(enabled=True)

    with pytest.raises(CampaignContainsSwearsError):
        await create_campaign.execute(
            advertiser_id=unique_advertiser.advertiser_id,
            data=CampaignCreateData(
                impressions_limit=100,
                clicks_limit=100,
                cost_per_impression=100,
                cost_per_click=100,
                ad_title="some",
                ad_text="some",
                start_date=0,
                end_date=100,
                targeting=CampaignTargeting(),
            ),
        )
