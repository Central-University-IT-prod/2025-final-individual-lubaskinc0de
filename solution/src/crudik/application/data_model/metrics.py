from pydantic import BaseModel


class ServiceMetrics(BaseModel):
    impressions_count: int
    clicks_count: int
    advertisers_count: int
    clients_count: int
    campaigns_count: int
    conversion: float
    income_impressions: float
    income_clicks: float
    income_total: float
