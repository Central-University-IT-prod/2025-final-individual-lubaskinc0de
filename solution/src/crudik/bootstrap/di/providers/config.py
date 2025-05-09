from dishka import Provider, Scope, provide

from crudik.adapters.config_loader import (
    Config,
    DBConnectionConfig,
    FilesConfig,
    YaGPTConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def config(self) -> Config:
        return Config.load_from_environment()

    @provide
    def db_connection(self, config: Config) -> DBConnectionConfig:
        return config.db_connection

    @provide
    def minio(self, config: Config) -> FilesConfig:
        return config.minio

    @provide
    def gpt(self, config: Config) -> YaGPTConfig:
        return config.gpt
