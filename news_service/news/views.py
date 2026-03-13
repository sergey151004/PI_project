from django.shortcuts import render
from .services.news_facade import NewsFacade


def news_list(request):

    news = NewsFacade.get_news()

    return render(request, "news.html", {"news": news})