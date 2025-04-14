from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID


class TargetGender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"


@dataclass
class Campaign:
    campaign_id: UUID
    advertiser_id: UUID
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    age_from: int | None = None
    age_to: int | None = None
    location: str | None = None
    gender: TargetGender | None = None
    image_path: str | None = None
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def is_started(self, day: int) -> bool:
        return day >= self.start_date

    def is_end(self, day: int) -> bool:
        return day > self.end_date

    def can_access(self) -> bool:
        return not self.is_deleted
