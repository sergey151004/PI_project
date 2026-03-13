from django.contrib import admin
from django.urls import path
from news.views import news_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', news_list),
]