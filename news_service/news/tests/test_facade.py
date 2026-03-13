from django.test import TestCase
from news.services.news_facade import NewsFacade


class NewsFacadeTest(TestCase):

    def test_create_news_should_create_news(self):

        news = NewsFacade.create_news(
            title="Facade title",
            text="Facade text"
        )

        self.assertEqual(news.title, "Facade title")

    def test_get_news_should_return_news_list(self):

        NewsFacade.create_news(
            title="News 1",
            text="Text 1"
        )

        NewsFacade.create_news(
            title="News 2",
            text="Text 2"
        )

        news_list = NewsFacade.get_news()

        self.assertEqual(len(news_list), 2)