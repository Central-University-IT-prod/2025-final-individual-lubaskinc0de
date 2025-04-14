import logging
from dataclasses import dataclass
from uuid import UUID, uuid4

from crudik.application.common.gateway.ad import AdGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.client import ClientGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.uow import UoW
from crudik.application.data_model.ad import Ad
from crudik.application.exceptions.ad import CannotShowAdError
from crudik.application.exceptions.client import ClientDoesNotExistsError
from crudik.domain.entity.impression import Impression


@dataclass(slots=True, frozen=True)
class ShowAd:
    client_gateway: ClientGateway
    day_gateway: DayGateway
    ad_gateway: AdGateway
    campaign_gateway: CampaignGateway
    uow: UoW

    async def execute(self, client_id: UUID) -> Ad:
        client = await self.client_gateway.get_by_id(client_id)
        if client is None:
            raise ClientDoesNotExistsError

        current_day = await self.day_gateway.read_current_day()
        ad = await self.ad_gateway.show_ad(client, current_day)

        if ad is None:
            raise CannotShowAdError

        campaign = await self.campaign_gateway.get_by_id(ad.ad_id)
        if campaign is None:
            logging.critical("Campaign is NULL when showing ad! ad_id = %s", ad.ad_id)
            raise CannotShowAdError

        impression = Impression(
            impression_id=uuid4(),
            ad_id=ad.ad_id,
            client_id=client_id,
            cost_per_impression=campaign.cost_per_impression,
            day=current_day,
        )
        self.uow.add(impression)
        await self.uow.commit()

        return ad
