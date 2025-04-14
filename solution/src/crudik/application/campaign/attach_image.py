from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID

from crudik.application.common.file_manager import FileManager
from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.uow import UoW
from crudik.application.data_model.campaign import CampaignImageData
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.campaign import CampaignDoesNotExistsError
from crudik.domain.error.base import AccessDeniedError


@dataclass(slots=True, frozen=True)
class AttachImageToCampaign:
    campaign_gateway: CampaignGateway
    advertiser_gateway: AdvertiserGateway
    file_manager: FileManager
    uow: UoW

    async def execute(
        self,
        campaign_id: UUID,
        advertiser_id: UUID,
        file: BinaryIO,
        ext: str,
        size: int,
    ) -> CampaignImageData:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        campaign = await self.campaign_gateway.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        if campaign.advertiser_id != advertiser_id:
            raise AccessDeniedError

        file_path = await self.file_manager.upload(file, ext, size)
        campaign.image_path = file_path

        await self.uow.commit()
        return CampaignImageData(
            campaign_id=campaign_id,
            path=file_path,
        )
