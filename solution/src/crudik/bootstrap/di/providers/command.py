from dishka import Provider, Scope, provide_all

from crudik.application.ad.click import ClickAd
from crudik.application.ad.show_ad import ShowAd
from crudik.application.advertiser.metrics import ProduceAdvertiserDailyStat, ProduceAdvertiserStat
from crudik.application.advertiser.read import ReadAdvertiser
from crudik.application.advertiser.upsert import UpsertAdvertisers
from crudik.application.campaign.attach_image import AttachImageToCampaign
from crudik.application.campaign.create import CreateCampaign
from crudik.application.campaign.delete import DeleteCampaign
from crudik.application.campaign.generate_ad_text import GenerateAdText
from crudik.application.campaign.list import ListCampaigns
from crudik.application.campaign.metrics import ProduceCampaignStat, ProduceCampaignStatDaily
from crudik.application.campaign.read import ReadCampaign
from crudik.application.campaign.update import UpdateCampaign
from crudik.application.client.read import ReadClient
from crudik.application.client.upsert import UpsertClients
from crudik.application.healthcheck import Healthcheck
from crudik.application.metrics import ProduceMetrics
from crudik.application.relevance.upsert import UpsertRelevance
from crudik.application.set_day import SetDay


class CommandProvider(Provider):
    scope = Scope.REQUEST

    commands = provide_all(
        Healthcheck,
        UpsertClients,
        ReadClient,
        UpsertAdvertisers,
        ReadAdvertiser,
        UpsertRelevance,
        CreateCampaign,
        DeleteCampaign,
        ReadCampaign,
        ListCampaigns,
        SetDay,
        UpdateCampaign,
        ShowAd,
        AttachImageToCampaign,
        ClickAd,
        ProduceCampaignStat,
        ProduceAdvertiserStat,
        ProduceMetrics,
        ProduceCampaignStatDaily,
        ProduceAdvertiserDailyStat,
        GenerateAdText,
    )
