from django.test import TestCase
from news.services.news_factory import NewsFactory
from news.models import News


class NewsFactoryTest(TestCase):

    def test_create_news_should_create_news_object(self):

        news = NewsFactory.create_news(
            title="Test title",
            text="Test text"
        )

        self.assertEqual(news.title, "Test title")
        self.assertEqual(news.text, "Test text")

        self.assertEqual(News.objects.count(), 1)