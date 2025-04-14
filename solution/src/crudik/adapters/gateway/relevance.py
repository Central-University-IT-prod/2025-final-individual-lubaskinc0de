from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.application.common.gateway.relevance import RelevanceGateway
from crudik.domain.entity.relevance import Relevance


@dataclass(slots=True, frozen=True)
class RelevanceAlchemyGateway(RelevanceGateway):
    session: AsyncSession

    async def upsert(self, data: Relevance) -> None:
        stmt = pg_insert(Relevance).values(
            client_id=data.client_id,
            advertiser_id=data.advertiser_id,
            score=data.score,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["client_id", "advertiser_id"],
            set_={
                "score": stmt.excluded.score,
            },
        )

        await self.session.execute(stmt)
