from uuid import UUID

from adaptix.conversion import get_converter
from pydantic import BaseModel

from crudik.domain.entity.advertiser import Advertiser


class AdvertiserData(BaseModel):
    advertiser_id: UUID
    name: str


convert_advertiser_to_entity = get_converter(AdvertiserData, Advertiser)
