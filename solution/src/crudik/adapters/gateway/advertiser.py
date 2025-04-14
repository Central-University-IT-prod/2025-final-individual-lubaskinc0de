from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.adapters.db.models.ad import campaign_table, click_table, impression_table
from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily, retort_campaign_stat_from_list
from crudik.domain.entity.advertiser import Advertiser
from crudik.domain.entity.campaign import Campaign


@dataclass(slots=True, frozen=True)
class AdvertiserAlchemyGateway(AdvertiserGateway):
    session: AsyncSession

    async def upsert(self, data: Iterable[Advertiser]) -> Sequence[Advertiser]:
        values = [
            {
                "advertiser_id": each.advertiser_id,
                "name": each.name,
            }
            for each in data
        ]

        stmt = pg_insert(Advertiser).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["advertiser_id"],
            set_={
                "name": stmt.excluded.name,
            },
        ).returning(Advertiser)  # type: ignore

        result = (await self.session.execute(stmt)).scalars().all()
        return result

    async def get_by_id(self, unique_id: UUID) -> Advertiser | None:
        q = select(Advertiser).filter_by(advertiser_id=unique_id)
        res = (await self.session.execute(q)).scalar_one_or_none()
        return res

    async def get_stat(self, advertiser_id: UUID) -> CampaignStat | None:
        impressions = (
            select(
                func.count().label("impressions_count"),
                func.coalesce(func.sum(impression_table.c.cost_per_impression), 0.0).label("spent_impressions"),
            )
            .join(Campaign, impression_table.c.ad_id == campaign_table.c.campaign_id)
            .where(campaign_table.c.advertiser_id == advertiser_id)
            .select_from(impression_table)
        ).cte()

        clicks = (
            select(
                func.count().label("clicks_count"),
                func.coalesce(func.sum(click_table.c.cost_per_click), 0.0).label("spent_clicks"),
            )
            .join(Campaign, click_table.c.ad_id == campaign_table.c.campaign_id)
            .where(campaign_table.c.advertiser_id == advertiser_id)
            .select_from(click_table)
        ).cte()

        impression_count = impressions.c.impressions_count
        click_count = clicks.c.clicks_count

        conversion = func.coalesce(
            (click_count / func.nullif(impression_count, 0)) * 100,
            0.0,
        )
        spent_impressions = impressions.c.spent_impressions
        spent_clicks = clicks.c.spent_clicks
        spent_total = spent_impressions + spent_clicks

        q = select(
            impression_count,
            click_count,
            conversion,
            spent_impressions,
            spent_clicks,
            spent_total,
        )
        result = await self.session.execute(q)
        row = result.first()

        if row is None:
            return None

        return retort_campaign_stat_from_list.load(row, CampaignStat)

    async def get_stat_daily(self, advertiser_id: UUID) -> Sequence[CampaignStatDaily]:
        impressions = (
            select(
                impression_table.c.day.label("day"),
                func.sum(impression_table.c.cost_per_impression).label("spent_impressions"),
                func.count().label("impressions_count"),
            )
            .join(campaign_table, impression_table.c.ad_id == campaign_table.c.campaign_id)
            .where(campaign_table.c.advertiser_id == advertiser_id)
            .group_by(impression_table.c.day)
            .select_from(impression_table)
        ).cte()

        clicks = (
            select(
                click_table.c.day.label("day"),
                func.sum(click_table.c.cost_per_click).label("spent_clicks"),
                func.count().label("clicks_count"),
            )
            .join(campaign_table, click_table.c.ad_id == campaign_table.c.campaign_id)
            .where(campaign_table.c.advertiser_id == advertiser_id)
            .group_by(click_table.c.day)
            .select_from(click_table)
        ).cte()

        impressions_count = func.coalesce(impressions.c.impressions_count, 0)
        clicks_count = func.coalesce(clicks.c.clicks_count, 0)
        spent_impressions = func.coalesce(impressions.c.spent_impressions, 0.0)
        spent_clicks = func.coalesce(clicks.c.spent_clicks, 0.0)
        conversion = case(
            (impressions_count > 0, (clicks_count / impressions_count) * 100),
            else_=0.0,
        )
        spent_total = spent_impressions + spent_clicks
        current_day = func.coalesce(clicks.c.day, impressions.c.day)
        q = (
            select(
                impressions_count,
                clicks_count,
                conversion,
                spent_impressions,
                spent_clicks,
                spent_total,
                current_day,
            )
            .select_from(impressions)
            .join(clicks, impressions.c.day == clicks.c.day, full=True)
            .order_by(current_day)
        )
        result = await self.session.execute(q)
        rows = result.all()

        res: Sequence[CampaignStatDaily] = retort_campaign_stat_from_list.load(rows, Sequence[CampaignStatDaily])
        return res
