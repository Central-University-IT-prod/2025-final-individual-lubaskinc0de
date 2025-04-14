import os
import random
from collections.abc import AsyncIterable, AsyncIterator
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import aiohttp
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.adapters.gateway.day import DAY_KEY
from crudik.adapters.swear_filter import CACHE_SWEARS_KEY, ENABLED_KEY
from crudik.bootstrap.di.container import get_async_container
from tests.e2e.models import (
    AdModel,
    AdvertiserModel,
    CampaignCreateModel,
    CampaignModel,
    CampaignUpdateModel,
    ClientGenderModel,
    ClientModel,
    ImageAttachResponseModel,
    RelevanceModel,
    TargetingGenderModel,
    TargetingModel,
)
from tests.fixtures.file_loader import ImportLibResourceLoader


@pytest.fixture
async def container() -> AsyncIterator[AsyncContainer]:
    container = get_async_container()
    yield container
    await container.close()


@pytest.fixture
async def session(container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    async with container() as r:
        yield (await r.get(AsyncSession))


@pytest.fixture
async def redis(container: AsyncContainer) -> Redis:
    return await container.get(Redis)


@pytest.fixture(autouse=True)
async def gracefully_teardown(
    session: AsyncSession,
    redis: Redis,
) -> AsyncIterable[None]:
    yield
    await session.execute(
        text("""
            DO $$
            DECLARE
                tb text;
            BEGIN
                FOR tb IN (
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                      AND tablename != 'alembic_version'
                )
                LOOP
                    EXECUTE 'TRUNCATE TABLE ' || tb || ' CASCADE';
                END LOOP;
            END $$;
        """),
    )
    await session.commit()
    await redis.set(DAY_KEY, "0")
    await redis.set(ENABLED_KEY, "0")
    await redis.set(CACHE_SWEARS_KEY, "{}")


@pytest.fixture
async def http_session() -> AsyncIterator[ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(scope="session")
def url() -> str:
    return os.environ["API_URL"]


@pytest.fixture
def valid_advertiser_data() -> list[AdvertiserModel]:
    return [
        AdvertiserModel(
            advertiser_id=UUID("0def01d6-1997-4b2f-a9c3-47b54d319344"),
            name="ООО Бнал",
        ),
        AdvertiserModel(
            advertiser_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
            name="ООО Банкротились",
        ),
        AdvertiserModel(
            advertiser_id=UUID("733f786c-171d-4403-b69a-8506cc49afa7"),
            name="ООО Майгад",
        ),
        AdvertiserModel(
            advertiser_id=UUID("b5086774-6d11-4206-9853-534b9b3cc404"),
            name="ООО Капец",
        ),
    ]


@pytest.fixture
async def created_advertisers(
    http_session: ClientSession,
    url: str,
    valid_advertiser_data: list[AdvertiserModel],
) -> list[AdvertiserModel]:
    endpoint = f"{url}/advertisers/bulk"
    data = [adv.model_dump(mode="json") for adv in valid_advertiser_data]
    async with http_session.post(endpoint, json=data) as response:
        return [AdvertiserModel(**item) for item in await response.json()]


@pytest.fixture
async def unique_advertiser(
    http_session: ClientSession,
    url: str,
    valid_advertiser_data: list[AdvertiserModel],
) -> AdvertiserModel:
    endpoint = f"{url}/advertisers/bulk"
    data = valid_advertiser_data[0].model_copy(
        update={"advertiser_id": uuid4()},
    )

    async with http_session.post(
        endpoint,
        json=[data.model_dump(mode="json")],
    ) as response:
        return AdvertiserModel(**(await response.json())[0])


@pytest.fixture
async def unique_client(
    http_session: ClientSession,
    url: str,
    valid_client_data: list[ClientModel],
) -> ClientModel:
    endpoint = f"{url}/clients/bulk"
    data = valid_client_data[0].model_copy(
        update={"client_id": uuid4()},
    )

    async with http_session.post(
        endpoint,
        json=[data.model_dump(mode="json")],
    ) as response:
        return ClientModel(**(await response.json())[0])


async def create_unique_client(
    http_session: ClientSession,
    url: str,
) -> ClientModel:
    endpoint = f"{url}/clients/bulk"
    data = ClientModel(
        client_id=uuid4(),
        login="some",
        age=25,
        location="Москва",
        gender=ClientGenderModel.MALE,
    )
    async with http_session.post(
        endpoint,
        json=[data.model_dump(mode="json")],
    ) as response:
        return ClientModel(**(await response.json())[0])


async def create_unique_advertiser(
    http_session: ClientSession,
    url: str,
) -> AdvertiserModel:
    endpoint = f"{url}/advertisers/bulk"
    data = AdvertiserModel(advertiser_id=uuid4(), name="ООО Бнал")

    async with http_session.post(
        endpoint,
        json=[data.model_dump(mode="json")],
    ) as response:
        return AdvertiserModel(**(await response.json())[0])


async def set_relevance(
    http_session: ClientSession,
    url: str,
    advertiser_id: UUID,
    client_id: UUID,
    score: int,
) -> None:
    endpoint = f"{url}/ml-scores"
    data = RelevanceModel(client_id=client_id, advertiser_id=advertiser_id, score=score)

    await http_session.post(
        endpoint,
        json=data.model_dump(mode="json"),
    )


async def update_campaign(
    http_session: ClientSession,
    url: str,
    campaign: CampaignModel,
    update: dict[Any, Any],
) -> CampaignModel:
    endpoint = f"{url}/advertisers/{campaign.advertiser_id}/campaigns/{campaign.campaign_id}"
    updated = campaign.model_copy(update=update)
    payload = CampaignUpdateModel(**(updated.model_dump()))

    async with http_session.put(
        endpoint,
        json=payload.model_dump(mode="json"),
    ) as response:
        data = CampaignModel(**(await response.json()))
        return data


@pytest.fixture
def valid_client_data() -> list[ClientModel]:
    return [
        ClientModel(
            client_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            login="user1",
            age=25,
            location="Москва",
            gender=ClientGenderModel.MALE,
        ),
        ClientModel(
            client_id=UUID("db81a812-93ef-47fa-aab7-23f35b568a34"),
            login="user2",
            age=30,
            location="Москва",
            gender=ClientGenderModel.FEMALE,
        ),
    ]


@pytest.fixture
async def created_clients(
    http_session: ClientSession,
    url: str,
    valid_client_data: list[ClientModel],
) -> list[ClientModel]:
    endpoint = f"{url}/clients/bulk"
    data = [client.model_dump(mode="json") for client in valid_client_data]
    async with http_session.post(endpoint, json=data) as response:
        return [ClientModel(**item) for item in await response.json()]


@pytest.fixture
async def created_campaigns(
    http_session: ClientSession,
    url: str,
    created_advertisers: list[AdvertiserModel],
    campaign_valid_data: CampaignCreateModel,
) -> list[CampaignModel]:
    objects = []

    for i in range(2):
        advertiser_id = created_advertisers[i].advertiser_id
        endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

        async with http_session.post(
            endpoint,
            json=campaign_valid_data.model_dump(mode="json"),
        ) as response:
            objects.append(CampaignModel(**await response.json()))

    return objects


@pytest.fixture
async def created_campaign(
    http_session: ClientSession,
    url: str,
    campaign_valid_data: CampaignCreateModel,
    unique_advertiser: AdvertiserModel,
) -> CampaignModel:
    advertiser_id = unique_advertiser.advertiser_id
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

    async with http_session.post(
        endpoint,
        json=campaign_valid_data.model_dump(mode="json"),
    ) as response:
        return CampaignModel(**await response.json())


@pytest.fixture
def image(resource_loader: ImportLibResourceLoader) -> tuple[Path, str]:
    choice = ["campaign/cat.jpg", "campaign/cat_1.jpg"]
    return resource_loader.get_full_path(Path(random.choice(choice))), "image/jpg"  # noqa: S311


@pytest.fixture
def images(resource_loader: ImportLibResourceLoader) -> list[tuple[Path, str]]:
    img = ["campaign/cat.jpg", "campaign/cat_1.jpg"]
    paths: list[tuple[Path, str]] = [(resource_loader.get_full_path(Path(i)), "image/jpg") for i in img]

    return paths


@pytest.fixture
def txt(resource_loader: ImportLibResourceLoader) -> tuple[Path, str]:
    return resource_loader.get_full_path(Path("some.txt")), "text/plain"


@pytest.fixture
def large_txt(resource_loader: ImportLibResourceLoader) -> tuple[Path, str]:
    return resource_loader.get_full_path(Path("25mb.txt")), "text/plain"


@pytest.fixture
def large_image(resource_loader: ImportLibResourceLoader) -> tuple[Path, str]:
    return resource_loader.get_full_path(Path("25mb.jpg")), "image/jpg"


async def create_campaign(
    http_session: ClientSession,
    url: str,
    advertiser_id: str,
    data: CampaignCreateModel,
) -> CampaignModel:
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns"

    async with http_session.post(
        endpoint,
        json=data.model_dump(mode="json"),
    ) as response:
        return CampaignModel(**await response.json())


async def attach_image(
    http_session: ClientSession,
    url: str,
    advertiser_id: str,
    campaign_id: str,
    image_path: Path,
    content_type: str,
) -> ImageAttachResponseModel:
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}/attach"

    data = aiohttp.FormData()
    with image_path.open("rb") as f:
        data.add_field("file", f, filename=f.name, content_type=content_type)

        async with http_session.put(endpoint, data=data) as response:
            json = await response.json()
            return ImageAttachResponseModel(**json)


async def create_campaign_with_image(
    http_session: ClientSession,
    url: str,
    advertiser_id: str,
    data: CampaignCreateModel,
    image_path: Path,
    content_type: str,
) -> CampaignModel:
    campaign = await create_campaign(http_session, url, advertiser_id, data)
    image_response = await attach_image(
        http_session,
        url,
        advertiser_id,
        str(campaign.campaign_id),
        image_path,
        content_type,
    )
    campaign.image_path = image_response.path

    return campaign


async def delete_campaign(
    http_session: ClientSession,
    url: str,
    advertiser_id: str,
    campaign_id: str,
) -> None:
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    await http_session.delete(endpoint)


@pytest.fixture
def campaign_valid_data() -> CampaignCreateModel:
    return CampaignCreateModel(
        impressions_limit=1000,
        clicks_limit=1000,
        cost_per_impression=float(random.randint(5, 10)),  # noqa: S311
        cost_per_click=float(random.randint(1, 5)),  # noqa: S311
        ad_title="Campaign",
        ad_text="some",
        start_date=0,
        end_date=7,
        targeting=TargetingModel(
            age_from=0,
            age_to=100,
            location="Москва",
            gender=TargetingGenderModel.ALL,
        ),
    )


@pytest.fixture
async def shown_campaign(
    http_session: ClientSession,
    url: str,
    unique_advertiser: AdvertiserModel,
    campaign_valid_data: CampaignCreateModel,
    unique_client: ClientModel,
) -> CampaignModel:
    campaign = await create_campaign(http_session, url, str(unique_advertiser.advertiser_id), campaign_valid_data)
    endpoint = f"{url}/ads?client_id={unique_client.client_id}"

    await http_session.get(endpoint)
    return campaign


def campaign_to_ad(campaign: CampaignModel) -> AdModel:
    return AdModel(
        ad_id=campaign.campaign_id,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        advertiser_id=campaign.advertiser_id,
    )


async def show_campaign(
    http_session: ClientSession,
    url: str,
    client_id: UUID,
) -> AdModel:
    endpoint = f"{url}/ads?client_id={client_id}"
    async with await http_session.get(endpoint) as r:
        json = await r.json()
        ad = AdModel(**json)
        return ad


async def click_campaign(
    http_session: ClientSession,
    url: str,
    client_id: UUID,
    campaign_id: UUID,
) -> None:
    endpoint = f"{url}/ads/{campaign_id}/click"

    await http_session.post(
        endpoint,
        json={"client_id": str(client_id)},
    )
