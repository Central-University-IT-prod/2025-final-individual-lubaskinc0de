from typing import NotRequired, TypedDict

import pytest
from aiohttp import ClientSession

from tests.e2e.status import OK, UNPROCESSABLE_ENTITY


class DayPayload(TypedDict):
    current_date: NotRequired[int]


async def test_valid(
    http_session: ClientSession,
    url: str,
) -> None:
    endpoint = f"{url}/time/advance"
    payload: DayPayload = {"current_date": 0}

    async with http_session.post(endpoint, json=payload) as response:
        assert response.status == OK
        data = await response.json()

        assert data == payload


async def test_empty(
    http_session: ClientSession,
    url: str,
) -> None:
    endpoint = f"{url}/time/advance"
    payload: DayPayload = {}

    async with http_session.post(endpoint, json=payload) as response:
        assert response.status == OK
        data = await response.json()

        assert data == {
            "current_date": 0,
        }


@pytest.mark.parametrize(
    ("day", "current_day"),
    [
        (-1, 0),
        (2, 3),
    ],
)
async def test_invalid(
    http_session: ClientSession,
    url: str,
    day: int,
    current_day: int,
) -> None:
    endpoint = f"{url}/time/advance"
    async with http_session.post(
        endpoint,
        json={"current_date": current_day},
    ) as response:
        assert response.status == OK

    payload: DayPayload = {"current_date": day}
    async with http_session.post(endpoint, json=payload) as response:
        assert response.status == UNPROCESSABLE_ENTITY
