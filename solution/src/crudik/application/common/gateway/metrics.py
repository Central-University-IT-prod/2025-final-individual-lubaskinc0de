from abc import abstractmethod
from typing import Protocol

from crudik.application.data_model.metrics import ServiceMetrics


class MetricsGateway(Protocol):
    @abstractmethod
    async def get_metrics(self) -> ServiceMetrics: ...
