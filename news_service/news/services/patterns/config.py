from typing import Optional, List, Dict
import os
from django.conf import settings


class NewsConfig:
    """
    Singleton — глобальная конфигурация новостного сервиса
    Один экземпляр на весь процесс Django
    """

    _instance: Optional['NewsConfig'] = None

    def __new__(cls) -> 'NewsConfig':
        if cls._instance is None:
            cls._instance = super(NewsConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        # Основные настройки — можно брать из settings, .env или БД в будущем
        self.sources: List[Dict] = [
            {
                "name": "Lenta.ru",
                "type": "rss",
                "url": "https://lenta.ru/rss",
                "max_items": 10,
            },
            {
                "name": "BBC News",
                "type": "rss",
                "url": "http://feeds.bbci.co.uk/news/rss.xml",
                "max_items": 8,
            },
            # Можно легко добавить JSON API, например:
            # {
            #     "name": "Some JSON API",
            #     "type": "json",
            #     "url": "https://api.example.com/news",
            #     "max_items": 5,
            # }
        ]

        # Таймауты и кэширование
        self.request_timeout: float = 8.0               # секунд
        self.cache_ttl_seconds: int = 600               # 10 минут
        self.max_news_items_per_request: int = 15

        # Пути и заголовки
        self.user_agent: str = "NewsService/1.0 (Django Microservice)"

    # Удобные свойства / методы

    @property
    def rss_sources(self) -> List[Dict]:
        return [s for s in self.sources if s["type"] == "rss"]

    def get_source_by_name(self, name: str) -> Optional[Dict]:
        for source in self.sources:
            if source["name"].lower() == name.lower():
                return source
        return None

    def __repr__(self) -> str:
        return f"<NewsConfig sources={len(self.sources)}>"


# Глобальная точка доступа (рекомендуемый способ использования)
news_config = NewsConfig()