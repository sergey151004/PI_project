from ..models import News
from .news_factory import NewsFactory
from .observers import notify


class NewsFacade:

    @staticmethod
    def create_news(title, text):

        news = NewsFactory.create_news(title, text)

        notify(news)

        return news

    @staticmethod
    def get_news():

        return News.objects.all().order_by("-created_at")