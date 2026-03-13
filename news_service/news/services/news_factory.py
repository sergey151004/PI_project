from news.models import News


class NewsFactory:

    @staticmethod
    def create_news(title, text):

        news = News.objects.create(
            title=title,
            text=text
        )

        return news