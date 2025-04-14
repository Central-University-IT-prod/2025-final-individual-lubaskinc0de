from dataclasses import dataclass
from uuid import UUID


@dataclass
class Advertiser:
    advertiser_id: UUID
    name: str
