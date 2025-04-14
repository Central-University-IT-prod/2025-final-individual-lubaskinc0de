from dataclasses import dataclass
from uuid import UUID


@dataclass
class Relevance:
    client_id: UUID
    advertiser_id: UUID
    score: int
