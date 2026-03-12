from django.urls import path
from .views import GradeList

urlpatterns = [
    path('grades/', GradeList.as_view()),
]