from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.adapters.db.models.ad import campaign_table, click_table, impression_table
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily, retort_campaign_stat_from_list
from crudik.domain.entity.campaign import Campaign
from crudik.domain.entity.click import Click
from crudik.domain.entity.impression import Impression


@dataclass(slots=True, frozen=True)
class CampaignAlchemyGateway(CampaignGateway):
    session: AsyncSession

    async def _get_by_id(self, unique_id: UUID) -> Campaign | None:
        q = select(Campaign).filter_by(campaign_id=unique_id)
        res = (await self.session.execute(q)).scalar_one_or_none()
        return res

    async def get_by_id(self, unique_id: UUID) -> Campaign | None:
        res = await self._get_by_id(unique_id)
        if res is None or res.is_deleted:
            return None

        return res

    async def get_by_id_all(self, unique_id: UUID) -> Campaign | None:
        res = await self._get_by_id(unique_id)
        if res is None:
            return None

        return res

    async def list(
        self,
        advertiser_id: UUID,
        limit: int | None,
        offset: int | None,
    ) -> Sequence[Campaign]:
        q = select(Campaign).filter_by(advertiser_id=advertiser_id, is_deleted=False)

        if limit is not None:
            q = q.limit(limit)

        if offset is not None:
            q = q.offset(offset)

        q = q.order_by(campaign_table.c.ad_title, campaign_table.c.campaign_id)

        response = await self.session.execute(q)
        return response.scalars().all()

    async def get_stat(self, unique_id: UUID) -> CampaignStat | None:
        impressions = (
            select(Impression)
            .where(impression_table.c.ad_id == campaign_table.c.campaign_id)
            .correlate(campaign_table)
            .subquery()
        )
        clicks = (
            select(Click)
            .where(click_table.c.ad_id == campaign_table.c.campaign_id)
            .correlate(campaign_table)
            .subquery()
        )
        impression_count = select(func.count()).select_from(impressions).scalar_subquery()
        click_count = select(func.count()).select_from(clicks).scalar_subquery()
        conversion = func.coalesce(
            (click_count / func.nullif(impression_count, 0)) * 100,
            0.0,
        )
        spent_impressions = func.coalesce(select(func.sum(impressions.c.cost_per_impression)).scalar_subquery(), 0.0)
        spent_clicks = func.coalesce(select(func.sum(clicks.c.cost_per_click)).scalar_subquery(), 0.0)
        spent_total = spent_impressions + spent_clicks

        q = (
            select(
                impression_count,
                click_count,
                conversion,
                spent_impressions,
                spent_clicks,
                spent_total,
            )
            .select_from(campaign_table)
            .where(
                campaign_table.c.campaign_id == unique_id,
            )
        )
        result = await self.session.execute(q)
        row = result.first()

        if row is None:
            return None

        return retort_campaign_stat_from_list.load(row, CampaignStat)

    async def get_stat_daily(self, unique_id: UUID) -> Sequence[CampaignStatDaily]:
        impressions = (
            select(
                impression_table.c.day.label("day"),
                func.sum(impression_table.c.cost_per_impression).label("spent_impressions"),
                func.count().label("impressions_count"),
            )
            .where(impression_table.c.ad_id == unique_id)
            .group_by(impression_table.c.day)
        ).cte()

        clicks = (
            select(
                click_table.c.day.label("day"),
                func.sum(click_table.c.cost_per_click).label("spent_clicks"),
                func.count().label("clicks_count"),
            )
            .where(click_table.c.ad_id == unique_id)
            .group_by(click_table.c.day)
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
