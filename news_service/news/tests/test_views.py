from django.test import TestCase
from news.models import News


class NewsViewTest(TestCase):

    def test_news_page_should_return_200(self):

        response = self.client.get("/news/")

        self.assertEqual(response.status_code, 200)

    def test_news_page_should_display_news(self):

        News.objects.create(
            title="Test news",
            text="Some text"
        )

        response = self.client.get("/news/")

        self.assertContains(response, "Test news")