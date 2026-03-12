from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login
from django.conf import settings
from django.views.decorators.http import require_http_methods

import requests
from requests.exceptions import RequestException

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from knox.views import LoginView as KnoxLoginView
from knox.models import AuthToken

from .models import User
from .serializers import UserSerializer
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from knox.models import AuthToken


# ────────────────────────────────────────────────
# API Views (для REST API)
# ────────────────────────────────────────────────
from django.shortcuts import render


@require_http_methods(["GET", "POST"])
def login_form_view(request):
    if request.method == 'GET':
        return render(request, 'users/login.html')

    # POST
    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username or not password:
        messages.error(request, "Укажите логин и пароль")
        return render(request, 'users/login.html')

    user = authenticate(request, username=username, password=password)
    if user is None:
        messages.error(request, "Неверный логин или пароль")
        return render(request, 'users/login.html')

    django_login(request, user)

    # Если используешь Knox — создаём токен (опционально)
    if 'knox_token' in request.session:  # или всегда
        AuthToken.objects.create(user)

    messages.success(request, f"Добро пожаловать, {user.username}!")
    return redirect('index')
class UserList(ListCreateAPIView):
    """
    Список и создание пользователей (только для авторизованных)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class SecureLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Используем request.POST, потому что форма — HTML, а не JSON
        username = request.POST.get('username')
        password = request.POST.get('password')

        print("=== POST данные ===")  # ← для отладки
        print(f"username: {username}")
        print(f"password: {password}")

        if not username or not password:
            messages.error(request, "Укажите логин и пароль")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        print(f"authenticate вернул: {user}")  # ← отладка

        if user is None:
            messages.error(request, "Неверный логин или пароль")
            return redirect('login')

        # Успех
        django_login(request, user)
        _, token = AuthToken.objects.create(user)
        request.session['knox_token'] = token
        request.session.modified = True

        messages.success(request, f"Добро пожаловать, {user.username}!")
        print("→ Редирект на index")  # ← отладка
        return redirect('index')


# ────────────────────────────────────────────────
# Шаблонные представления (для фронтенда на Django templates)
# ────────────────────────────────────────────────

def index(request):
    """Главная страница"""
    context = {
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, 'users/index.html', context)


@require_http_methods(["GET"])
def grades_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # ← здесь 'login', а не 'api-login'

    token = request.session.get('knox_token')
    print(f"Токен из сессии: {token}")  # ← если None — проблема

    headers = {'Authorization': f'Token {token}'} if token else {}
    print(f"Headers для запросов: {headers}")

    courses_url = f"{settings.COURSES_API_BASE}courses/"
    print(f"Запрос курсов: {courses_url}")

    grades_url = f"{settings.GRADES_API_BASE}grades/?student_id={request.user.id}"
    print(f"Запрос оценок: {grades_url}")
    print(f"ID текущего пользователя: {request.user.id}")

    courses = []
    grades = []

    try:
        resp = requests.get(courses_url, headers=headers, timeout=6)
        print(f"Курсы: status={resp.status_code}, content={resp.text[:200]}")
        if resp.ok:
            courses = resp.json()
    except Exception as e:
        print(f"Ошибка курсов: {e}")

    try:
        resp = requests.get(grades_url, headers=headers, timeout=6)
        print(f"Оценки: status={resp.status_code}, content={resp.text[:200]}")
        if resp.ok:
            grades = resp.json()
    except Exception as e:
        print(f"Ошибка оценок: {e}")

    context = {
        'courses': courses,
        'grades': grades,
        'current_user': request.user,
    }
    return render(request, 'users/grades.html', context)


# ────────────────────────────────────────────────
# Опционально: простой выход из системы
# ────────────────────────────────────────────────

def logout_view(request):
    """Выход пользователя"""
    from django.contrib.auth import logout
    logout(request)
    request.session.flush()           # очищаем токен Knox из сессии
    return redirect('index')