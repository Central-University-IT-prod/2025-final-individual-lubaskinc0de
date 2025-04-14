from pathlib import Path

import aiohttp
from aiohttp import ClientSession

from tests.e2e.conftest import create_campaign_with_image, delete_campaign
from tests.e2e.models import (
    AdvertiserModel,
    CampaignCreateModel,
    CampaignModel,
    ImageAttachResponseModel,
)
from tests.e2e.status import BAD_REQUEST, NOT_FOUND, OK, TOO_LARGE


async def test_attach_image(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
    image: tuple[Path, str],
) -> None:
    src = created_campaigns[0]
    advertiser_id = src.advertiser_id
    campaign_id = src.campaign_id
    image_path, content_type = image
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}/attach"

    data = aiohttp.FormData()
    with image_path.open("rb") as f:
        data.add_field("file", f, filename=f.name, content_type=content_type)

        async with http_session.put(endpoint, data=data) as response:
            assert response.status == OK
            json = await response.text(encoding="utf-8")
            ImageAttachResponseModel.model_validate_json(json)


async def test_attach_image_to_deleted(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
    image: tuple[Path, str],
) -> None:
    src = created_campaigns[0]
    advertiser_id = src.advertiser_id
    campaign_id = src.campaign_id
    await delete_campaign(http_session, url, str(advertiser_id), str(campaign_id))

    image_path, content_type = image
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}/attach"

    data = aiohttp.FormData()
    with image_path.open("rb") as f:
        data.add_field("file", f, filename=f.name, content_type=content_type)

        async with http_session.put(endpoint, data=data) as response:
            assert response.status == NOT_FOUND


async def test_update_attachment(
    http_session: ClientSession,
    url: str,
    images: list[tuple[Path, str]],
    unique_advertiser: AdvertiserModel,
    campaign_valid_data: CampaignCreateModel,
) -> None:
    img_one = images[0]
    img_two = images[1]

    src = await create_campaign_with_image(
        http_session,
        url,
        str(unique_advertiser.advertiser_id),
        campaign_valid_data,
        *img_one,
    )
    first_img = src.image_path
    endpoint_read = f"{url}/advertisers/{unique_advertiser.advertiser_id}/campaigns/{src.campaign_id}"

    async with http_session.get(endpoint_read) as response:
        assert response.status == OK
        json = await response.json()
        assert CampaignModel(**json) == src

    endpoint_attach = f"{url}/advertisers/{unique_advertiser.advertiser_id}/campaigns/{src.campaign_id}/attach"
    image_path, content_type = img_two
    data = aiohttp.FormData()
    with image_path.open("rb") as f:
        data.add_field("file", f, filename=f.name, content_type=content_type)

        async with http_session.put(endpoint_attach, data=data) as response:
            assert response.status == OK
            json = await response.json()
            resp = ImageAttachResponseModel(**json)
            dest = src.model_copy(update={"image_path": resp.path})
            second_img = dest.image_path

    async with http_session.get(endpoint_read) as response:
        assert response.status == OK
        json = await response.json()
        assert CampaignModel(**json) == dest
        assert first_img != second_img


async def test_attach_txt(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
    txt: tuple[Path, str],
) -> None:
    src = created_campaigns[0]
    advertiser_id = src.advertiser_id
    campaign_id = src.campaign_id
    image_path, content_type = txt
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}/attach"

    data = aiohttp.FormData()
    with image_path.open("rb") as f:
        data.add_field("file", f, filename=f.name, content_type=content_type)

        async with http_session.put(endpoint, data=data) as response:
            assert response.status == BAD_REQUEST


async def test_too_large(
    http_session: ClientSession,
    url: str,
    created_campaigns: list[CampaignModel],
    large_image: tuple[Path, str],
) -> None:
    src = created_campaigns[0]
    advertiser_id = src.advertiser_id
    campaign_id = src.campaign_id
    image_path, content_type = large_image
    endpoint = f"{url}/advertisers/{advertiser_id}/campaigns/{campaign_id}/attach"

    data = aiohttp.FormData()
    with image_path.open("rb") as f:
        data.add_field("file", f, filename=f.name, content_type=content_type)

        async with http_session.put(endpoint, data=data) as response:
            assert response.status == TOO_LARGE
