from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.ad_text_generator import AdTextGenerator
from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.data_model.campaign import GenerateAdTextResponse
from crudik.application.exceptions.advertiser import AdvertiserDoesNotExistsError


@dataclass(slots=True, frozen=True)
class GenerateAdText:
    advertiser_gateway: AdvertiserGateway
    generator: AdTextGenerator

    async def execute(
        self,
        ad_title: str,
        advertiser_id: UUID,
    ) -> GenerateAdTextResponse:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        ad_text = await self.generator.generate_ad_text(advertiser.name, ad_title)
        return GenerateAdTextResponse(
            ad_text=ad_text,
        )
