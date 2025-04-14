from abc import abstractmethod
from typing import Protocol


class AdTextGenerator(Protocol):
    @abstractmethod
    async def generate_ad_text(self, advertiser_name: str, ad_title: str) -> str: ...
