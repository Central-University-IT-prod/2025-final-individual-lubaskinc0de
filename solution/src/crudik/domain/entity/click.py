from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class Click:
    click_id: UUID
    ad_id: UUID
    client_id: UUID
    cost_per_click: float
    day: int
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
