from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.application.common.gateway.client import ClientGateway
from crudik.domain.entity.client import Client


@dataclass(slots=True, frozen=True)
class ClientAlchemyGateway(ClientGateway):
    session: AsyncSession

    async def upsert(self, data: Iterable[Client]) -> Sequence[Client]:
        values = [
            {
                "client_id": client.client_id,
                "login": client.login,
                "age": client.age,
                "location": client.location,
                "gender": client.gender,
            }
            for client in data
        ]

        stmt = pg_insert(Client).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["client_id"],
            set_={
                "login": stmt.excluded.login,
                "age": stmt.excluded.age,
                "location": stmt.excluded.location,
                "gender": stmt.excluded.gender,
            },
        ).returning(Client)  # type: ignore

        result = (await self.session.execute(stmt)).scalars().all()
        return result

    async def get_by_id(self, unique_id: UUID) -> Client | None:
        q = select(Client).filter_by(client_id=unique_id)
        res = (await self.session.execute(q)).scalar_one_or_none()
        return res
