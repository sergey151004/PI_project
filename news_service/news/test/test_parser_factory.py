from django.test import TestCase

from ..services.patterns.parsers.base_parser import NewsParser
from ..services.patterns.parsers.factory import NewsParserFactory
from ..services.patterns.config import news_config


class ParserFactoryTestCase(TestCase):
    def test_factory_creates_rss_parsers(self):
        parsers = NewsParserFactory.create_parsers_for_all_sources()

        self.assertEqual(len(parsers), len(news_config.sources))
        self.assertTrue(all(isinstance(p, NewsParser) for p in parsers))
        self.assertTrue(all(p.get_source_name() in ['Lenta.ru', 'BBC News'] for p in parsers))

        print("Фабрика создала парсеры корректно")