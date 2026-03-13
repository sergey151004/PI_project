# news/test/test_config.py

from django.test import TestCase

# относительный импорт от корня приложения news
from ..services.patterns.config import news_config


class ConfigTestCase(TestCase):
    def test_singleton_works(self):
        config1 = news_config
        config2 = news_config

        self.assertIs(config1, config2)
        self.assertEqual(len(config1.sources), 2)
        self.assertTrue(all("url" in s for s in config1.sources))
        print("Singleton работает корректно")