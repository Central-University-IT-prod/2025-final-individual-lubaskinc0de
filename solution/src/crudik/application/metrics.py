import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from adaptix import Retort

from crudik.application.common.cache_storage import KeyValueStorage
from crudik.application.common.gateway.metrics import MetricsGateway
from crudik.application.data_model.metrics import ServiceMetrics

CACHE_SECONDS = 5
METRICS_CACHE_KEY = "metrics"
CACHE_UNTIL_KEY = "cache_until"

retort = Retort()


@dataclass(slots=True, frozen=True)
class ProduceMetrics:
    gateway: MetricsGateway
    storage: KeyValueStorage

    async def execute(self) -> ServiceMetrics:
        now = datetime.now(tz=UTC)
        is_cached = False
        cache = await self.storage.get(METRICS_CACHE_KEY)
        cache_entry = None
        cache_until = None

        if cache:
            cache_dict = json.loads(cache)
            cache_until_entry = cache_dict[CACHE_UNTIL_KEY]
            cache_until = datetime.fromtimestamp(cache_until_entry, tz=UTC)
            if now < cache_until:
                is_cached = True
                cache_entry = retort.load(cache_dict, ServiceMetrics)

        if is_cached and cache_entry is not None:
            logging.info("Cached get metrics")
            return cache_entry

        logging.info("No cache for metrics")
        metrics = await self.gateway.get_metrics()
        cache_new_until = (now + timedelta(seconds=CACHE_SECONDS)).timestamp()
        cache_new_entry: dict[Any, Any] = retort.dump(metrics)
        cache_new_entry[CACHE_UNTIL_KEY] = cache_new_until

        await self.storage.set(METRICS_CACHE_KEY, json.dumps(cache_new_entry))
        return metrics
