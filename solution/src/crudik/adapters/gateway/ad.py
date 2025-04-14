from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import (
    and_,
    case,
    exists,
    func,
    literal,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.adapters.db.models.ad import (
    campaign_table,
    click_table,
    impression_table,
    relevance_table,
)
from crudik.application.common.gateway.ad import AdGateway
from crudik.application.data_model.ad import Ad
from crudik.domain.entity.campaign import TargetGender
from crudik.domain.entity.click import Click
from crudik.domain.entity.client import Client
from crudik.domain.entity.impression import Impression


@dataclass(slots=True, frozen=True)
class AdAlchemyGateway(AdGateway):
    session: AsyncSession

    async def get_impression(self, client_id: UUID, ad_id: UUID) -> Impression | None:
        q = select(Impression).filter_by(client_id=client_id, ad_id=ad_id)
        res = (await self.session.execute(q)).scalar_one_or_none()
        return res

    async def get_click(self, client_id: UUID, ad_id: UUID) -> Click | None:
        q = select(Click).filter_by(client_id=client_id, ad_id=ad_id)
        res = (await self.session.execute(q)).scalar_one_or_none()
        return res

    async def get_clicks_count(self, ad_id: UUID) -> int:
        q = select(func.count("*")).where(click_table.c.ad_id == ad_id).select_from(click_table)
        res = (await self.session.execute(q)).scalar_one()
        return res

    async def show_ad(self, client: Client, day: int) -> Ad | None:
        impression_cte = (
            select(impression_table.c.ad_id, func.count().label("count"))
            .group_by(impression_table.c.ad_id)
            .cte("impression_counts")
        )

        click_cte = (
            select(click_table.c.ad_id, func.count().label("count")).group_by(click_table.c.ad_id).cte("click_counts")
        )

        profit = 0.5 * (campaign_table.c.cost_per_impression + campaign_table.c.cost_per_click)
        relevance = 0.25 * func.coalesce(relevance_table.c.score, 0)

        impressions_ratio = func.coalesce(impression_cte.c.count, 0) / campaign_table.c.impressions_limit
        clicks_ratio = func.coalesce(click_cte.c.count, 0) / campaign_table.c.clicks_limit
        limit_bonus = 0.15 * ((1 - impressions_ratio) + (1 - clicks_ratio)) / 2
        click_penalty = case(
            (
                click_cte.c.count > campaign_table.c.clicks_limit,
                -0.05 * clicks_ratio,
            ),
            else_=0.0,
        )
        query = (
            select(
                campaign_table.c.campaign_id,
                campaign_table.c.ad_text,
                campaign_table.c.ad_title,
                campaign_table.c.advertiser_id,
            )
            .outerjoin(
                relevance_table,
                and_(
                    relevance_table.c.client_id == client.client_id,
                    relevance_table.c.advertiser_id == campaign_table.c.advertiser_id,
                ),
            )
            .outerjoin(impression_cte, impression_cte.c.ad_id == campaign_table.c.campaign_id)
            .outerjoin(click_cte, click_cte.c.ad_id == campaign_table.c.campaign_id)
            .where(
                and_(
                    campaign_table.c.start_date <= day,
                    campaign_table.c.end_date >= day,
                    or_(campaign_table.c.age_from.is_(None), campaign_table.c.age_from <= client.age),
                    or_(campaign_table.c.age_to.is_(None), campaign_table.c.age_to >= client.age),
                    or_(campaign_table.c.location.is_(None), campaign_table.c.location == client.location),
                    or_(
                        campaign_table.c.gender.is_(None),
                        campaign_table.c.gender == TargetGender.ALL,
                        and_(campaign_table.c.gender == TargetGender.MALE, literal(client.gender.value) == "MALE"),
                        and_(campaign_table.c.gender == TargetGender.FEMALE, literal(client.gender.value) == "FEMALE"),
                    ),
                    ~exists().where(
                        and_(
                            impression_table.c.client_id == client.client_id,
                            impression_table.c.ad_id == campaign_table.c.campaign_id,
                        ),
                    ),
                    func.coalesce(impression_cte.c.count, 0) < campaign_table.c.impressions_limit * 1.049,
                    ~campaign_table.c.is_deleted,
                ),
            )
            .order_by((profit + relevance + limit_bonus + click_penalty).desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        row = result.first()
        return Ad(row[0], row[1], row[2], row[3]) if row else None
