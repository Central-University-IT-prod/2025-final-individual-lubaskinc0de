from collections.abc import AsyncIterator

from aiohttp import ClientSession
from dishka import AnyOf, Provider, Scope, provide
from miniopy_async import Minio  # type:ignore[import-untyped]
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.adapters.config_loader import DBConnectionConfig, FilesConfig
from crudik.adapters.db.provider import (
    get_async_session,
    get_async_sessionmaker,
    get_engine,
)
from crudik.adapters.file_manager import MinioFileManager
from crudik.adapters.redis import RedisStorage
from crudik.adapters.swear_filter import LLMSwearFilter
from crudik.adapters.text_generator import LLMAdTextGenerator
from crudik.application.common.ad_text_generator import AdTextGenerator
from crudik.application.common.cache_storage import KeyValueStorage
from crudik.application.common.file_manager import FileManager
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.common.uow import UoW


class AdapterProvider(Provider):
    redis_storage = provide(RedisStorage, provides=AnyOf[RedisStorage, KeyValueStorage], scope=Scope.APP)
    swear_filter = provide(
        LLMSwearFilter,
        provides=SwearFilter,
        scope=Scope.APP,
    )
    text_generator = provide(
        LLMAdTextGenerator,
        provides=AdTextGenerator,
        scope=Scope.APP,
    )
    file_manager = provide(
        MinioFileManager,
        provides=FileManager,
        scope=Scope.APP,
    )

    @provide(scope=Scope.APP)
    async def redis_client(
        self,
        config: DBConnectionConfig,
    ) -> AsyncIterator[Redis]:
        redis = Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=0,
        )
        yield redis
        await redis.aclose()

    @provide(scope=Scope.APP)
    async def minio_client(self, config: FilesConfig) -> AsyncIterator[Minio]:
        client = Minio(
            config.minio_url,
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=False,
        )
        yield client

    @provide(scope=Scope.APP)
    async def client_session(self) -> AsyncIterator[ClientSession]:
        async with ClientSession() as session:
            yield session


def adapter_provider() -> AdapterProvider:
    provider = AdapterProvider()
    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(
        get_async_session,
        provides=AnyOf[AsyncSession, UoW],
        scope=Scope.REQUEST,
    )

    return provider
