from abc import ABC, abstractmethod
from typing import List, Dict, Any


class NewsParser(ABC):
    """Базовый интерфейс для всех парсеров новостей"""

    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict]:
        """
        Принимает сырые данные (rss-feed, json и т.д.)
        Возвращает список словарей в едином формате
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Имя источника, которое будет записано в новость"""
        pass