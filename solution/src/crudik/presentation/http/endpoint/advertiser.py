from collections.abc import Sequence
from uuid import UUID

import filetype  # type: ignore
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from crudik.application.advertiser.read import ReadAdvertiser
from crudik.application.advertiser.upsert import UpsertAdvertisers
from crudik.application.campaign.attach_image import AttachImageToCampaign
from crudik.application.campaign.create import CreateCampaign
from crudik.application.campaign.delete import DeleteCampaign
from crudik.application.campaign.generate_ad_text import GenerateAdText
from crudik.application.campaign.list import ListCampaigns
from crudik.application.campaign.read import ReadCampaign
from crudik.application.campaign.update import UpdateCampaign
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.data_model.advertiser import AdvertiserData
from crudik.application.data_model.campaign import (
    CampaignCreateData,
    CampaignData,
    CampaignImageData,
    CampaignUpdateData,
    GenerateAdTextResponse,
)
from crudik.application.data_model.common import Pagination
from crudik.domain.entity.advertiser import Advertiser
from crudik.presentation.http.exceptions import (
    CannotReadFileInfoError,
    CannotReadFileSizeError,
    FileIsNotImageError,
    FileTooBigError,
)

router = APIRouter(
    tags=["Advertisers"],
    route_class=DishkaRoute,
    prefix="/advertisers",
)
MAX_FILE_SIZE = 20 * 1024 * 1024


class ToggleSwearsCheckBody(BaseModel):
    check_enabled: bool


@router.put("/toggle/swears", status_code=204)
async def toggle_swears_check(data: ToggleSwearsCheckBody, swear_filter: FromDishka[SwearFilter]) -> None:
    await swear_filter.set_mode(enabled=data.check_enabled)


@router.post("/bulk", status_code=201)
async def bulk(
    command: FromDishka[UpsertAdvertisers],
    data: list[AdvertiserData],
) -> Sequence[Advertiser]:
    return await command.execute(data)


@router.get("/{entry_id}")
async def read(
    command: FromDishka[ReadAdvertiser],
    entry_id: UUID,
) -> Advertiser:
    return await command.execute(entry_id)


@router.post(
    "/{advertiser_id}/campaigns",
    status_code=201,
    response_model_exclude_none=True,
)
async def create_campaign(
    command: FromDishka[CreateCampaign],
    data: CampaignCreateData,
    advertiser_id: UUID,
) -> CampaignData:
    return await command.execute(data, advertiser_id)


@router.get("/{advertiser_id}/campaigns/generate")
async def generate_ad_text(
    command: FromDishka[GenerateAdText],
    ad_title: str,
    advertiser_id: UUID,
) -> GenerateAdTextResponse:
    return await command.execute(ad_title, advertiser_id)


@router.delete("/{advertiser_id}/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(
    command: FromDishka[DeleteCampaign],
    advertiser_id: UUID,
    campaign_id: UUID,
) -> None:
    return await command.execute(
        advertiser_id=advertiser_id,
        campaign_id=campaign_id,
    )


@router.get(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response_model_exclude_none=True,
)
async def read_campaign(
    command: FromDishka[ReadCampaign],
    advertiser_id: UUID,
    campaign_id: UUID,
) -> CampaignData:
    return await command.execute(
        advertiser_id=advertiser_id,
        campaign_id=campaign_id,
    )


@router.put(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response_model_exclude_none=True,
)
async def update_campaign(
    command: FromDishka[UpdateCampaign],
    advertiser_id: UUID,
    campaign_id: UUID,
    data: CampaignUpdateData,
) -> CampaignData:
    return await command.execute(
        advertiser_id=advertiser_id,
        campaign_id=campaign_id,
        data=data,
    )


@router.put("/{advertiser_id}/campaigns/{campaign_id}/attach")
async def upload_image(
    advertiser_id: UUID,
    campaign_id: UUID,
    command: FromDishka[AttachImageToCampaign],
    file: UploadFile,
) -> CampaignImageData:
    if not file.size:
        raise CannotReadFileSizeError

    if file.size > MAX_FILE_SIZE:
        raise FileTooBigError

    file_info = filetype.guess(await file.read(128))
    if file_info is None:
        raise CannotReadFileInfoError

    mime, ext = file_info.mime, file_info.extension

    if not mime.startswith("image/"):
        raise FileIsNotImageError

    return await command.execute(
        campaign_id,
        advertiser_id,
        file.file,
        ext,
        file.size,
    )


@router.get("/{advertiser_id}/campaigns", response_model_exclude_none=True)
async def list_campaigns(
    command: FromDishka[ListCampaigns],
    advertiser_id: UUID,
    size: int | None = None,
    page: int | None = None,
) -> Sequence[CampaignData]:
    pagination = Pagination(
        size=size,
        page=page,
    )
    return await command.execute(advertiser_id, pagination)
