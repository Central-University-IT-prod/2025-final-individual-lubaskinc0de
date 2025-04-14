from dishka import Provider, Scope, provide

from crudik.adapters.gateway.ad import AdAlchemyGateway
from crudik.adapters.gateway.advertiser import AdvertiserAlchemyGateway
from crudik.adapters.gateway.campaign import CampaignAlchemyGateway
from crudik.adapters.gateway.client import ClientAlchemyGateway
from crudik.adapters.gateway.day import DayRedisGateway
from crudik.adapters.gateway.metrics import MetricsAlchemyGateway
from crudik.adapters.gateway.relevance import RelevanceAlchemyGateway
from crudik.application.common.gateway.ad import AdGateway
from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.client import ClientGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.gateway.metrics import MetricsGateway
from crudik.application.common.gateway.relevance import RelevanceGateway


class GatewayProvider(Provider):
    scope = Scope.REQUEST

    client_gateway = provide(ClientAlchemyGateway, provides=ClientGateway)
    advertiser_gateway = provide(
        AdvertiserAlchemyGateway,
        provides=AdvertiserGateway,
    )
    relevance_gateway = provide(
        RelevanceAlchemyGateway,
        provides=RelevanceGateway,
    )
    day_gateway = provide(DayRedisGateway, provides=DayGateway)
    campaign_gateway = provide(CampaignAlchemyGateway, provides=CampaignGateway)
    ad_gateway = provide(AdAlchemyGateway, provides=AdGateway)
    metrics_gateway = provide(MetricsAlchemyGateway, provides=MetricsGateway)
