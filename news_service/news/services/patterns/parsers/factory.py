from typing import Optional
from ..config import news_config
from .base_parser import NewsParser
from .rss_parser import RSSParser


class NewsParserFactory:
    """
    Factory Method — создаёт нужный парсер в зависимости от типа источника
    """

    @staticmethod
    def create_parser(source: dict) -> Optional[NewsParser]:
        source_type = source.get('type')
        source_name = source.get('name', 'Unknown')

        if source_type == 'rss':
            return RSSParser(source_name)

        # Здесь в будущем можно добавить другие типы
        # elif source_type == 'json':
        #     return JsonParser(source_name)
        # elif source_type == 'atom':
        #     return AtomParser(source_name)

        print(f"Неизвестный тип источника: {source_type}")
        return None

    @staticmethod
    def create_parsers_for_all_sources() -> list[NewsParser]:
        """Удобный метод — сразу все парсеры для всех источников"""
        parsers = []
        for source in news_config.sources:
            parser = NewsParserFactory.create_parser(source)
            if parser:
                parsers.append(parser)
        return parsers