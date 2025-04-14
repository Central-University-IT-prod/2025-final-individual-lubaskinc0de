import pytest

from crudik.application.campaign.create import CreateCampaign
from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.common.uow import UoW


@pytest.fixture
def create_campaign(
    uow: UoW,
    day_gateway: DayGateway,
    advertiser_gateway: AdvertiserGateway,
    campaign_gateway: CampaignGateway,
    swear_filter: SwearFilter,
) -> CreateCampaign:
    return CreateCampaign(uow, day_gateway, campaign_gateway, advertiser_gateway, swear_filter)
