from dataclasses import dataclass
from uuid import UUID, uuid4

from crudik.application.common.gateway.ad import AdGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.client import ClientGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.uow import UoW
from crudik.application.data_model.ad import ClickRequest
from crudik.application.exceptions.ad import CannotClickWithoutImpressionError
from crudik.application.exceptions.campaign import CampaignDoesNotExistsError
from crudik.application.exceptions.client import ClientDoesNotExistsError
from crudik.domain.entity.click import Click


@dataclass(slots=True, frozen=True)
class ClickAd:
    campaign_gateway: CampaignGateway
    ad_gateway: AdGateway
    client_gateway: ClientGateway
    day_gateway: DayGateway
    uow: UoW

    async def execute(
        self,
        request: ClickRequest,
        ad_id: UUID,
    ) -> None:
        client_id = request.client_id
        client = await self.client_gateway.get_by_id(client_id)
        if client is None:
            raise ClientDoesNotExistsError

        campaign = await self.campaign_gateway.get_by_id(ad_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        impression = await self.ad_gateway.get_impression(client_id, ad_id)
        if impression is None:
            raise CannotClickWithoutImpressionError

        prev_click = await self.ad_gateway.get_click(client_id, ad_id)
        if prev_click is not None:
            return

        current_day = await self.day_gateway.read_current_day()
        click = Click(
            click_id=uuid4(),
            ad_id=campaign.campaign_id,
            client_id=client_id,
            cost_per_click=campaign.cost_per_click,
            day=current_day,
        )
        self.uow.add(click)
        await self.uow.commit()
