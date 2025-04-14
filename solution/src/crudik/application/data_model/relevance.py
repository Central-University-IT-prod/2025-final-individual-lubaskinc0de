from uuid import UUID

from adaptix.conversion import get_converter
from pydantic import BaseModel

from crudik.application.data_model.common import PositiveIntZero
from crudik.domain.entity.relevance import Relevance


class RelevanceData(BaseModel):
    client_id: UUID
    advertiser_id: UUID
    score: PositiveIntZero


convert_relevance_to_entity = get_converter(RelevanceData, Relevance)
