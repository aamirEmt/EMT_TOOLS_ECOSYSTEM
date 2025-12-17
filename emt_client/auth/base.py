from abc import ABC, abstractmethod
from typing import Dict

class TokenProvider(ABC):

    @abstractmethod
    async def get_tokens(self) -> Dict[str, str]:
        """Return tokens required for the service"""
