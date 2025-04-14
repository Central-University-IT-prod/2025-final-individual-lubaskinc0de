from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class Ad:
    ad_id: UUID
    ad_text: str
    ad_title: str
    advertiser_id: UUID


@dataclass(slots=True, frozen=True)
class ClickRequest:
    client_id: UUID
