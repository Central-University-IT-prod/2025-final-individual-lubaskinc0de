from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Healthcheck:
    async def execute(self) -> str:
        return "pong"
