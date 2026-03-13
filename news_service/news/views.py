# news/views.py
from rest_framework.views import APIView
from rest_framework.response import Response


class NewsListView(APIView):
    """Временная заглушка — чтобы makemigrations прошёл"""
    def get(self, request):
        return Response({"message": "News service is alive"})