from uuid import UUID

from adaptix import Retort, name_mapping
from pydantic import BaseModel

from crudik.application.data_model.common import (
    Age,
    PositiveFloatZero,
    PositiveIntZero,
)
from crudik.domain.entity.campaign import Campaign, TargetGender


class CampaignTargeting(BaseModel):
    age_from: Age | None = None
    age_to: Age | None = None
    location: str | None = None
    gender: TargetGender | None = None


class CampaignCreateData(BaseModel):
    impressions_limit: PositiveIntZero
    clicks_limit: PositiveIntZero
    cost_per_impression: PositiveFloatZero
    cost_per_click: PositiveFloatZero
    ad_title: str
    ad_text: str
    start_date: PositiveIntZero
    end_date: PositiveIntZero
    targeting: CampaignTargeting | None = None


class GenerateAdTextResponse(BaseModel):
    ad_text: str


class CampaignData(CampaignCreateData):
    campaign_id: UUID
    advertiser_id: UUID
    image_path: str | None = None


class CampaignUpdateData(CampaignCreateData): ...


class CampaignImageData(BaseModel):
    campaign_id: UUID
    path: str


class CampaignStat(BaseModel):
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float


class CampaignStatDaily(CampaignStat):
    date: int


retort_campaign_stat_from_list = Retort(
    recipe=[
        name_mapping(
            CampaignStatDaily,
            as_list=True,
        ),
        name_mapping(
            CampaignStat,
            as_list=True,
        ),
    ],
    strict_coercion=False,
)


def convert_entity_to_campaign(data: Campaign) -> CampaignData:
    return CampaignData(
        campaign_id=data.campaign_id,
        advertiser_id=data.advertiser_id,
        impressions_limit=data.impressions_limit,
        clicks_limit=data.clicks_limit,
        cost_per_impression=data.cost_per_impression,
        cost_per_click=data.cost_per_click,
        ad_title=data.ad_title,
        ad_text=data.ad_text,
        start_date=data.start_date,
        end_date=data.end_date,
        targeting=CampaignTargeting(
            age_from=data.age_from,
            age_to=data.age_to,
            location=data.location,
            gender=data.gender,
        ),
        image_path=data.image_path,
    )
