import pytest

from tests.e2e.models import StatsModel


@pytest.fixture
def zero_stat() -> StatsModel:
    return StatsModel(
        impressions_count=0,
        clicks_count=0,
        conversion=0.0,
        spent_impressions=0.0,
        spent_clicks=0.0,
        spent_total=0.0,
    )
