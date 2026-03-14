# Code Review: PI_project

Отчёт выполнен по методологии Code Review: проверка реализации, логики, обработки ошибок, безопасности, тестирования и читаемости. Для каждого замечания приведён фрагмент кода, описание и рекомендация.

---

## 1. Реализация и архитектура

### 1.1 API курсов не подключён к корневому urlconf

**Файл:** `courses_service/courses_service/urls.py`

```python
urlpatterns = [
    path('admin/', admin.site.urls),
]
```

**Описание:** Приложение `courses` определяет маршруты `courses/` в `courses/urls.py`, но они нигде не подключены. В корневом `urls.py` нет `include('courses.urls')`.

**Замечание:** users_service ожидает API по адресу `COURSES_API_BASE + "courses/"` (т.е. `http://127.0.0.1:8081/api/courses/`). Сейчас этот эндпоинт недоступен — интеграция сломана.

**Рекомендация:** Добавить в `courses_service/urls.py` строку:
```python
path('api/', include('courses.urls')),
```

---

### 1.2 Дублирование импортов и разрозненная структура views

**Файл:** `users_service/users/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login
# ...
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from knox.models import AuthToken
# ... позже снова:
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
```

**Описание:** Один и тот же модуль импортируется несколько раз в разных местах файла; импорты перемешаны с объявлением классов и функций.

**Замечание:** Нарушается единый стиль (все импорты в начале), увеличивается шанс конфликтов и путаницы. Ухудшается читаемость.

**Рекомендация:** Собрать все импорты в начало файла, сгруппировать по стандарту (stdlib → Django → third-party → local). Удалить неиспользуемые (например, `RequestException`, `status`, `Response`, `KnoxLoginView`).

---

### 1.3 Дублирование кода модели User

**Файл:** `users_service/users/models.py`

```python
from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
```

**Описание:** Строка `from django.db import models` повторяется дважды.

**Замечание:** Мёртвый/дублирующий код, плохая подготовка к ревью.

**Рекомендация:** Оставить один блок импортов:
```python
from django.db import models
from django.contrib.auth.models import AbstractUser
```

---

## 2. Логика и граничные случаи

### 2.1 Логика создания токена в login_form_view

**Файл:** `users_service/users/views.py`

```python
django_login(request, user)
if 'knox_token' in request.session:  # или всегда
    AuthToken.objects.create(user)
```

**Описание:** Токен создаётся только если в сессии уже есть ключ `knox_token`. При первом заходе через форму логина сессии пусты, токен не создаётся.

**Замечание:** Логическая ошибка: условие обратное. После успешного логина токен нужно как раз создавать и класть в сессию (как в `SecureLoginView`), а не проверять его наличие до создания.

**Рекомендация:** Создавать токен после логина и сохранять в сессии, например:
```python
_, token = AuthToken.objects.create(user)
request.session['knox_token'] = token
request.session.modified = True
```

---

### 2.2 Отсутствие проверки типов/значений для внешних ID

**Файл:** `grades_service/grades/models.py`

```python
class Grade(models.Model):
    student_id = models.IntegerField()  # ID из Users Service
    course_id = models.IntegerField()   # ID из Courses Service
    grade = models.CharField(max_length=2)  # A, B, C и т.д.
```

**Описание:** Нет проверки, что `student_id` и `course_id` существуют в соответствующих сервисах; нет ограничения на допустимые значения `grade`.

**Замечание:** Можно сохранить несуществующие ID или некорректные оценки (пустая строка, длинное значение при обходе валидации). Граничные случаи не обрабатываются.

**Рекомендация:** Добавить в сериализатор или модель валидацию (например, `choices` для `grade`, или кастомный validator). Опционально — проверка существования ID в других сервисах при создании.

---

## 3. Ошибки и логирование

### 3.1 print вместо логирования

**Файл:** `users_service/users/views.py`

```python
print("=== POST данные ===")
print(f"username: {username}")
print(f"password: {password}")
# ...
print(f"authenticate вернул: {user}")
print("→ Редирект на index")
# в grades_view:
print(f"Токен из сессии: {token}")
print(f"Headers для запросов: {headers}")
print(f"Курсы: status={resp.status_code}, content={resp.text[:200]}")
print(f"Ошибка курсов: {e}")
```

**Описание:** Для отладки и «логирования» используется `print`. Пароль логируется в открытом виде.

**Замечание:** В продакшене print не управляется уровнем логирования, не пишется в файл/систему логов. Вывод пароля — утечка конфиденциальных данных и нарушение безопасности.

**Рекомендация:** Удалить все print. Использовать `logging` (например, `logger = logging.getLogger(__name__)`), не логировать пароли и токены; для отладочной информации использовать уровень `DEBUG` и отключать в production.

---

### 3.2 Слишком широкий except в grades_view

**Файл:** `users_service/users/views.py`

```python
try:
    resp = requests.get(courses_url, headers=headers, timeout=6)
    # ...
    if resp.ok:
        courses = resp.json()
except Exception as e:
    print(f"Ошибка курсов: {e}")
```

**Описание:** Перехватывается любое исключение; кроме сетевых ошибок могут «проглатываться» ошибки парсинга JSON, таймауты и т.д.

**Замечание:** Сложнее отлаживать; пользователь просто видит пустой список без понимания причины. Нет разделения на типы ошибок (сеть, 4xx/5xx, неверный JSON).

**Рекомендация:** Ловить конкретные исключения (`requests.RequestException`, `ValueError` для json). Логировать через `logging` с уровнем и текстом ошибки. При необходимости отдавать пользователю понятное сообщение (например, «Сервис курсов временно недоступен»).

---

## 4. Безопасность

### 4.1 Секретные ключи в коде

**Файлы:** `users_service/users_service/settings.py`, `courses_service/courses_service/settings.py`, `grades_service/grades_service/settings.py`, `news_service/news_service/settings.py`

```python
SECRET_KEY = 'django-insecure-^fy1s0p$g!+_wwi)zw3ia$n_p^7qe2-stuaa0jm=jhqdy$0(29'
```

**Описание:** SECRET_KEY захардкожен в настройках каждого сервиса; в репозитории есть файл `.env` с URL, но ключи из окружения не подставляются.

**Замечание:** Риск утечки секретов при публикации репозитория. Нет разделения конфигурации по средам (dev/prod). В статье по ревью указано: «отсутствие утечки секретов».

**Рекомендация:** Читать SECRET_KEY из переменных окружения (например, `os.environ.get('SECRET_KEY')`) или из `.env` через `python-dotenv`. В репозитории оставить только пример (`.env.example`) без реальных значений.

---

### 4.2 ALLOWED_HOSTS пустой

**Файл:** `users_service/users_service/settings.py` (и другие settings)

```python
ALLOWED_HOSTS = []
```

**Описание:** При пустом `ALLOWED_HOSTS` Django в production отклоняет запросы по Host; при `DEBUG=True` возможны предупреждения.

**Замечание:** Для локальной разработки часто добавляют `'127.0.0.1'`, `'localhost'`. В отчёте по безопасности это типичная проверка.

**Рекомендация:** Для dev явно указать, например: `ALLOWED_HOSTS = ['127.0.0.1', 'localhost']`, для production — брать из переменной окружения.

---

### 4.3 URL внешних сервисов захардкожены в settings

**Файл:** `users_service/users_service/settings.py`

```python
COURSES_API_BASE = "http://127.0.0.1:8081/api/"
GRADES_API_BASE  = "http://127.0.0.1:8082/api/"
```

**Описание:** В корне есть `.env` с `COURSES_URL` и `GRADES_URL`, но в settings они не используются — значения продублированы константами.

**Замечание:** При смене портов или хостов нужно править код; конфигурация не централизована. Риск рассинхрона между .env и кодом.

**Рекомендация:** Подгружать из окружения: `COURSES_API_BASE = os.environ.get('COURSES_URL', 'http://127.0.0.1:8081/api/')` (и аналогично для GRADES). Использовать `python-dotenv` в начале settings при необходимости.

---

## 5. Зависимости и конфигурация

### 5.1 requirements.txt без django-cors-headers

**Файл:** `requirements.txt`

В списке нет `django-cors-headers`. В части версий/форков проекта news_service может использовать `corsheaders` в `INSTALLED_APPS` и middleware.

**Замечание:** При установке только из `requirements.txt` возможна ошибка `ModuleNotFoundError: No module named 'corsheaders'` при запуске news_service (если там включён CORS).

**Рекомендация:** Если CORS в проекте используется — добавить `django-cors-headers` в `requirements.txt` с версией.

---

## 6. Читаемость и стиль

---

### 6.1 отсутствие docstring у классов/методов

**Файлы:** `courses_service/courses/views.py`, `grades_service/grades/views.py`, часть `news_service`

Пример:

```python
class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
```

**Описание:** У многих view-классов и функций нет описания назначения.

**Замечание:** Ухудшает понимание кода новыми разработчиками и при ревью. В статье указано: «адекватные комментарии», «понятная структура».

**Рекомендация:** Добавить краткие docstring к публичным view и ключевым функциям (что возвращают, какие права требуют).

---

## 7. Что сделано хорошо (без замечаний)

Ниже — элементы, которые соответствуют ожиданиям код-ревью и не требуют правок по текущему чек-листу.

- **Разделение сервисов:** Чёткое разделение на courses, grades, users, news — каждый со своей БД и зоной ответственности. Архитектура соответствует заявленной микросервисной схеме.

- **Использование DRF и Knox:** В users_service корректно подключены REST Framework и Knox, заданы `AUTH_USER_MODEL`, permission classes и класс аутентификации по токену. Реализация авторизации через Knox в `SecureLoginView` (создание токена и сохранение в сессии) логична и понятна.

- **Модели courses и grades:** Поля моделей `Course` и `Grade` названы понятно; в коде есть комментарии про связь ID с другими сервисами. Структура моделей простая и соответствует задаче.

- **Сериализаторы:** Использование `ModelSerializer` с `fields = '__all__'` или явным списком полей (UserSerializer с `['id', 'username', 'role']`) — уместно и без лишней сложности.

- **Паттерны в news_service:** Factory, Facade и Observer применены последовательно: создание новости через фабрику, единая точка входа через фасад, уведомление подписчиков через `notify()`. Регистрация наблюдателя в `apps.ready()` — корректный способ инициализации при старте приложения.

- **Тесты courses и grades:** В courses есть тесты модели и сериализатора; в grades — модели, сериализатора и API (GET/POST). Это даёт базовое покрытие критичной логики этих сервисов.

- **Шаблон news.html:** Структура HTML и стили адекватны, используется цикл по объектам и `{% empty %}`, без лишней сложности.

- **README:** В репозитории есть подробный README с описанием архитектуры, запуска и паттернов — это соответствует требованию к документации при ревью.

---

## Итоги Code Review

### ToDo (обязательные изменения)

1. Подключить API курсов в `courses_service/urls.py` через `path('api/', include('courses.urls'))`.
2. Убрать все `print` из `users_service/users/views.py`, не логировать пароли; перейти на модуль `logging`.
3. Исправить логику создания Knox-токена в `login_form_view` (создавать токен после логина и сохранять в сессии).
4. Удалить дублирование импортов и лишнюю строку `from django.db import models` в `users_service/users/models.py`.
5. Вынести SECRET_KEY и URL сервисов (COURSES_API_BASE, GRADES_API_BASE) в переменные окружения в users_service и при необходимости в других сервисах.

### Вопросы

1. Является ли намеренным отсутствие фильтрации оценок по `student_id` в grades_service (т.е. отдаём ли мы все оценки любому клиенту)?
2. Нужно ли сохранять единообразие входа: чтобы и форма логина, и API-логин одинаково создавали токен и клали его в сессию для последующих запросов к courses/grades?

### Предложения (улучшения без обязательности)

- Добавить фильтрацию `GradeList.get_queryset()` по `student_id` (и/или по токену пользователя).
- В `grades_view` ловить конкретные исключения при запросах к API и логировать через `logging`.
- Заполнить `ALLOWED_HOSTS` для dev (например, `'127.0.0.1'`, `'localhost'`).
- Добавить тесты для users_service: логин, доступ к `/grades/`, редиректы.
- Собрать импорты в начале `users/views.py` и удалить неиспользуемые.
- Добавить краткие docstring к основным view и фасаду/фабрике в news_service.
- Если в репозитории используется CORS в news_service — добавить `django-cors-headers` в `requirements.txt`.
