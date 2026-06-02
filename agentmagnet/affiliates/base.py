from abc import ABC, abstractmethod


class AffiliateProgram(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", country: str | None = None) -> list[dict]:
        pass

    @abstractmethod
    def get_commission_info(self) -> dict:
        pass
