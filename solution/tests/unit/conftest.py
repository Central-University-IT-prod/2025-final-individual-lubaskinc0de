from uuid import uuid4

import pytest

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.current_day import DayGateway, MockDayGateway
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.common.uow import UoW
from crudik.domain.entity.advertiser import Advertiser
from tests.unit.mocks import MockAdvertiserGateway, MockCampaignGateway, MockSwearFilter, MockUoW


@pytest.fixture
def day_gateway() -> DayGateway:
    return MockDayGateway()


@pytest.fixture
def campaign_gateway() -> CampaignGateway:
    return MockCampaignGateway()


@pytest.fixture
def advertiser_gateway() -> AdvertiserGateway:
    return MockAdvertiserGateway()


@pytest.fixture
def swear_filter() -> SwearFilter:
    return MockSwearFilter()


@pytest.fixture
def uow(advertiser_gateway: MockAdvertiserGateway, campaign_gateway: MockCampaignGateway) -> UoW:
    return MockUoW(
        campaign_mapper=campaign_gateway,
        advertiser_mapper=advertiser_gateway,
    )


@pytest.fixture
def unique_advertiser(uow: UoW) -> Advertiser:
    advertiser_id = uuid4()
    name = "ООО Бнал"
    advertiser = Advertiser(advertiser_id, name)
    uow.add(advertiser)
    return advertiser
