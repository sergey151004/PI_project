from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('grades/', views.grades_view, name='grades'),
    path('logout/', views.logout_view, name='logout'),

    # API
    path('login/', views.login_form_view, name='login'),
    path('api/users/', views.UserList.as_view(), name='api-users'),
    path('api/login/', views.SecureLoginView.as_view(), name='api-login'),
]