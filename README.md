# Система учета оценок

Учебный проект на базе микросервисной архитектуры: несколько независимых Django-приложений, общающихся по HTTP. Система охватывает пользователей, курсы, оценки и новости.

---

## Содержание

- [Обзор архитектуры](#обзор-архитектуры)
- [Технологии](#технологии)
- [Структура репозитория](#структура-репозитория)
- [Сервисы](#сервисы)
- [Установка и запуск](#установка-и-запуск)
- [Переменные окружения](#переменные-окружения)
- [API и порты](#api-и-порты)

---

## Обзор архитектуры

```
                    ┌─────────────────────────────────────────┐
                    │           users_service (8080)           │
                    │  Фронтенд, авторизация, агрегация данных │
                    └──────────────┬──────────────────────────┘
                                   │ HTTP (requests)
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ courses_service  │    │ grades_service   │    │  news_service     │
│     (8081)       │    │     (8082)      │    │     (8083)        │
│  Курсы           │    │  Оценки         │    │  Новости          │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

- **users_service** — точка входа для пользователя: логин, сессии, Knox-токены, страницы с оценками и главная. По HTTP запрашивает данные у courses и grades.
- **courses_service**, **grades_service**, **news_service** — отдельные Django-проекты со своими БД (SQLite), моделями и API/страницами.

---

## Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3, Django 6.0 |
| API | Django REST Framework |
| Аутентификация | django-rest-knox (токены) |
| HTTP-клиент | requests |
| Конфигурация | python-dotenv, переменные в settings |
| БД | SQLite (отдельная на каждый сервис) |

Зависимости перечислены в корневом `requirements.txt`; один общий виртуальный окружение используется для всех сервисов.

---

## Структура репозитория

```
PI_project/
├── .env                    # URL сервисов (courses, grades)
├── requirements.txt        # Общие зависимости
├── courses_service/        # Сервис курсов
│   ├── courses/            # Приложение: модели, views, serializers, urls
│   └── courses_service/    # Проект: settings, urls
├── grades_service/
│   ├── grades/
│   └── grades_service/
├── users_service/
│   ├── users/              # Модели User, views, шаблоны (login, index, grades)
│   └── users_service/
└── news_service/
    ├── news/               # Модель News, facade, factory, observers, шаблон
    └── news_service/
```

Виртуальное окружение (`.venv`) обычно создаётся в корне `PI_project` и не коммитится в репозиторий.

---

## Сервисы

### 1. courses_service (порт 8081)

**Назначение:** хранение и выдача списка курсов.

- **Модель:** `Course` — поля `name`, `description`.
- **API:** DRF `ListCreateAPIView` для курсов (список и создание). Роуты приложения: `courses/` (в приложении `courses`).
- **Важно:** в корневом `courses_service/urls.py` по умолчанию подключён только `admin/`. Чтобы users_service мог обращаться к API по адресу `http://127.0.0.1:8081/api/courses/`, в `courses_service/urls.py` нужно добавить:
  ```python
  path('api/', include('courses.urls')),
  ```
- **БД:** `courses_service/db.sqlite3`.

---

### 2. grades_service (порт 8082)

**Назначение:** хранение оценок студентов по курсам (связь по ID пользователя и ID курса из других сервисов).

- **Модель:** `Grade` — `student_id`, `course_id`, `grade` (например A, B, C).
- **API:** `GET/POST /api/grades/` (список и создание). Фильтрация по `student_id` через query-параметр: `?student_id=<id>`.
- **БД:** `grades_service/db.sqlite3`.

---

### 3. users_service (порт 8080 или 8000)

**Назначение:** пользователи, авторизация, фронтенд и агрегация данных из courses/grades.

- **Модель:** `User` (AbstractUser) — поле `role` (student/teacher).
- **Настройки:** `AUTH_USER_MODEL = 'users.User'`; в settings заданы `COURSES_API_BASE` и `GRADES_API_BASE` для HTTP-запросов к другим сервисам.
- **Маршруты:**
  - `/` — главная (index).
  - `/login/` — форма входа (GET/POST).
  - `/api/login/` — API-вход (POST), создаёт сессию и Knox-токен, редирект на главную.
  - `/api/users/` — список/создание пользователей (требуется аутентификация по токену).
  - `/grades/` — страница с курсами и оценками текущего пользователя (данные запрашиваются у courses и grades по `request.user.id` и токену из сессии).
  - `/logout/` — выход, сброс сессии.
- **БД:** `users_service/db.sqlite3`.

---

### 4. news_service (порт 8083)

**Назначение:** простой сервис новостей с паттернами Facade, Factory и Observer.

- **Модель:** `News` — `title`, `text`, `created_at`.
- **Логика:**
  - `NewsFactory` — создание записей `News`.
  - `NewsFacade` — единая точка: `create_news(title, text)` (создание + уведомление наблюдателей), `get_news()` (список по дате).
  - `observers` — список подписчиков; при создании новости вызывается `notify(news)` (например, `LoggerObserver` выводит заголовок в консоль).
- **Маршрут:** `GET /news/` — страница со списком новостей (шаблон `news.html`).
- **БД:** `news_service/db.sqlite3`.

---

## Установка и запуск

### 1. Клонирование и окружение

```bash
git clone https://github.com/sergey151004/PI_project.git
cd PI_project
```

Создать виртуальное окружение и установить зависимости:

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

При необходимости для news_service может понадобиться пакет `django-cors-headers` (если в проекте включён CORS):

```bash
pip install django-cors-headers
```

### 2. Переменные окружения

В корне проекта должен быть файл `.env` (или экспорт переменных в системе):

```env
COURSES_URL=http://127.0.0.1:8081/api/
GRADES_URL=http://127.0.0.1:8082/api/
```

Значения используются в users_service (в settings можно задать `COURSES_API_BASE` / `GRADES_API_BASE` из `.env` или напрямую).

### 3. Миграции

В каждом сервисе один раз выполнить:

```bash
cd courses_service && python manage.py migrate && cd ..
cd grades_service && python manage.py migrate && cd ..
cd users_service && python manage.py migrate && cd ..
cd news_service  && python manage.py migrate && cd ..
```

Или из корня с указанием пути к Python venv (Windows):

```powershell
.\.venv\Scripts\python.exe courses_service\manage.py migrate --settings=courses_service.settings
.\.venv\Scripts\python.exe grades_service\manage.py migrate --settings=grades_service.settings
.\.venv\Scripts\python.exe users_service\manage.py migrate --settings=users_service.settings
.\.venv\Scripts\python.exe news_service\manage.py migrate --settings=news_service.settings
```

Или заходя в каждую папку с активированным `.venv` и выполняя `python manage.py migrate`.

### 4. Создание суперпользователя (users_service)

```bash
cd users_service
python manage.py createsuperuser
```

### 5. Запуск сервисов

Запускать каждый сервис в отдельном терминале (с активированным `.venv`).

**Терминал 1 — courses:**

```bash
cd PI_project/courses_service
python manage.py runserver 8081
```

**Терминал 2 — grades:**

```bash
cd PI_project/grades_service
python manage.py runserver 8082
```

**Терминал 3 — users (точка входа для браузера):**

```bash
cd PI_project/users_service
python manage.py runserver 8080
```

**Терминал 4 — news:**

```bash
cd PI_project/news_service
python manage.py runserver 8083
```

После этого:

- Главная и логин: **http://127.0.0.1:8080/**
- Оценки (после входа): **http://127.0.0.1:8080/grades/**
- Новости: **http://127.0.0.1:8083/news/**
- API курсов (если в courses_service добавлен `path('api/', include('courses.urls'))`): **http://127.0.0.1:8081/api/courses/**
- API оценок: **http://127.0.0.1:8082/api/grades/**

---

## Переменные окружения

| Переменная | Где используется | Описание |
|------------|------------------|----------|
| `COURSES_URL` | .env, users_service | Базовый URL API курсов |
| `GRADES_URL`  | .env, users_service | Базовый URL API оценок |

В коде users_service обычно используются константы `COURSES_API_BASE` и `GRADES_API_BASE` (из settings или загруженные из `.env`).

---

## API и порты

| Сервис | Порт | Основные эндпоинты |
|--------|------|--------------------|
| users_service | 8080 | `/`, `/login/`, `/api/login/`, `/api/users/`, `/grades/`, `/logout/` |
| courses_service | 8081 | `/api/courses/` (если добавлен в urlconf) |
| grades_service | 8082 | `/api/grades/` |
| news_service | 8083 | `/news/` (HTML) |

Формат обмена с courses/grades — JSON (DRF). Аутентификация к API users — по заголовку `Authorization: Token <knox_token>`.

---

## Тестирование

Тесты запускаются в соответствующей папке сервиса (активированное venv и установленные зависимости).

**courses_service:**

```bash
cd courses_service
python manage.py test courses
```

Проверяются модель `Course`, сериализатор и (при наличии) API.

**grades_service:**

```bash
cd grades_service
python manage.py test grades
```

Проверяются модель `Grade`, сериализатор и API (GET/POST `/api/grades/`).

**users_service:**

```bash
cd users_service
python manage.py test users
```

**news_service:**

В приложении `news` тесты лежат в пакете `news.tests`. Чтобы Django их обнаруживал, в каталоге `news/tests/` должен быть файл `__init__.py` (пустой или с комментарием). Затем:

```bash
cd news_service
python manage.py test news
```

Проверяются фасад (`NewsFacade`), фабрика (`NewsFactory`) и вьюха списка новостей.

Запуск всех тестов по одному сервису:

```bash
cd <service_dir>
python manage.py test
```

---

## Краткая сводка по интеграции

1. **users_service** обращается к **courses_service** по `COURSES_API_BASE` + `courses/` и к **grades_service** по `GRADES_API_BASE` + `grades/?student_id=...`. Для этого courses_service должен отдавать API по префиксу `/api/` (добавить `path('api/', include('courses.urls'))` в его корневой `urls.py`).
2. Токен Knox после входа сохраняется в сессии и передаётся в заголовках при запросах к другим сервисам (если те ожидают авторизацию).
3. **news_service** пока не вызывается из users_service; к нему можно обращаться напрямую по порту 8083 или в дальнейшем добавить вызов из users (например, блок новостей на главной).


## Подробный разбор news_service и паттернов проектирования

Сервис новостей построен как отдельный Django-проект с явным использованием трёх паттернов проектирования: **Factory**, **Facade** и **Observer**. Ниже — структура сервиса, назначение каждого паттерна и поток данных.

---

### Назначение и структура сервиса

**news_service** отвечает за:

- хранение новостей (модель `News`: заголовок, текст, дата);
- создание новостей через единую точку входа с уведомлением подписчиков;
- отдачу списка новостей на страницу `/news/`.

Структура приложения `news`:

```
news_service/
├── news/
│   ├── models.py           # Модель News
│   ├── views.py            # Вьюха news_list — отдаёт страницу со списком
│   ├── urls.py             # (нет отдельного файла, роуты в news_service/urls.py)
│   ├── admin.py            # Регистрация News в админке
│   ├── apps.py             # Регистрация наблюдателей при старте (ready)
│   ├── services/
│   │   ├── news_factory.py  # Паттерн Factory — создание объекта News
│   │   ├── news_facade.py   # Паттерн Facade — единая точка входа
│   │   └── observers.py    # Паттерн Observer — список подписчиков и notify
│   ├── templates/
│   │   └── news.html       # Шаблон страницы «School News»
│   └── tests/              # Тесты фасада, фабрики и вьюхи
└── news_service/
    ├── settings.py
    └── urls.py             # path('news/', news_list)
```

Маршрут: **GET** `http://127.0.0.1:8083/news/` — единственная публичная страница; создание новостей через фасад (код или админку).

---

### Модель данных

```python
# news/models.py
class News(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

- **title** — заголовок новости.
- **text** — полный текст.
- **created_at** — дата и время создания (проставляется автоматически).

Сортировка при выдаче списка: от новых к старым (`order_by("-created_at")` в фасаде).

---

### Паттерн 1: Factory (Фабрика)

**Файл:** `news/services/news_factory.py`

**Идея паттерна:** вынос логики создания объекта в отдельный класс/метод. Вызывающий код не вызывает конструктор и не знает деталей инициализации (поля, значения по умолчанию, побочные эффекты).

**В проекте:**

- Класс `NewsFactory` с одним статическим методом `create_news(title, text)`.
- Внутри — `News.objects.create(title=..., text=...)`, возвращается экземпляр `News`.
- Вся логика «как именно создаётся новость» сосредоточена в одном месте; при изменении полей модели правится только фабрика.

```python
class NewsFactory:
    @staticmethod
    def create_news(title, text):
        news = News.objects.create(title=title, text=text)
        return news
```

Использование: фасад вызывает именно `NewsFactory.create_news(...)`, а не `News.objects.create(...)` напрямую.

---

### Паттерн 2: Facade (Фасад)

**Файл:** `news/services/news_facade.py`

**Идея паттерна:** предоставить простой единый интерфейс к подсистеме (нескольким классам или шагам). Клиент общается только с фасадом и не зависит от фабрики, наблюдателей и т.д.

**В проекте:**

- Класс `NewsFacade` — единственная точка входа для бизнес-операций с новостями.
  - **create_news(title, text)** — создать новость (через фабрику) и уведомить всех наблюдателей (`notify(news)`), затем вернуть созданный объект.
  - **get_news()** — вернуть все новости, отсортированные по дате (новые первые).

Вьюха не обращается к модели или фабрике напрямую: только `NewsFacade.get_news()`. Создание новостей в коде тоже идёт через `NewsFacade.create_news(...)`, чтобы срабатывали наблюдатели.

```python
class NewsFacade:
    @staticmethod
    def create_news(title, text):
        news = NewsFactory.create_news(title, text)
        notify(news)
        return news

    @staticmethod
    def get_news():
        return News.objects.all().order_by("-created_at")
```

Поток при создании: **клиент → Facade.create_news → Factory.create_news → notify(observers)**.

---

### Паттерн 3: Observer (Наблюдатель)

**Файл:** `news/services/observers.py`

**Идея паттерна:** объекты-наблюдатели подписываются на события; при наступлении события источник вызывает их общий метод (например, `update(data)`). Так можно добавлять логирование, рассылки, обновление кэша и т.п. без изменения кода создания новости.

**В проекте:**

- **Список подписчиков:** глобальный список `observers`.
- **register(observer)** — добавить наблюдателя в список. У каждого наблюдателя должен быть метод `update(news)`.
- **notify(news)** — пройти по всем зарегистрированным наблюдателям и вызвать `observer.update(news)`.
- **LoggerObserver** — пример наблюдателя: в `update(self, news)` выводит в консоль `"New article:"` и заголовок новости.

Регистрация наблюдателей выполняется при старте приложения в `apps.py`:

```python
# news/apps.py
class NewsConfig(AppConfig):
    def ready(self):
        from .services.observers import register, LoggerObserver
        register(LoggerObserver())
```

Таким образом, при каждом создании новости через `NewsFacade.create_news()` после сохранения в БД вызывается `notify(news)`, и все подписчики (сейчас только `LoggerObserver`) получают объект новости и могут выполнить свои действия (логирование, отправка в мессенджер и т.д.).

---

### Поток данных при создании новости

1. Вызов `NewsFacade.create_news(title, text)` (из кода, админки или будущего API).
2. Фасад вызывает `NewsFactory.create_news(title, text)` → в БД создаётся запись `News`.
3. Фасад вызывает `notify(news)`.
4. В `observers.py` цикл по списку `observers`: для каждого вызывается `observer.update(news)`.
5. Например, `LoggerObserver().update(news)` печатает заголовок в консоль.
6. Фасад возвращает созданный объект `news`.

При отображении страницы `/news/` поток проще: вьюха вызывает `NewsFacade.get_news()`, получает QuerySet новостей и передаёт его в шаблон `news.html`.

---

### Вьюха и шаблон

- **views.py:** одна функция `news_list(request)`: получает список через `NewsFacade.get_news()`, рендерит `news.html` с контекстом `{"news": news}`.
- **news.html:** заголовок страницы «School News», цикл по `news` — для каждой записи выводится карточка (заголовок, дата `created_at`, текст). При пустом списке — «No news yet.»

Админка: модель `News` зарегистрирована в `admin.site.register(News)`; создание/редактирование в админке не идёт через фасад, поэтому наблюдатели при создании из админки не вызываются (при желании это можно доработать через переопределение `ModelAdmin.save_model` и вызов фасада/notify).

---

### Как добавить нового наблюдателя

1. В `news/services/observers.py` создать класс с методом `update(self, news)`:

   ```python
   class EmailObserver:
       def update(self, news):
           # отправить письмо о новой новости
           pass
   ```

2. В `news/apps.py` в методе `ready()` зарегистрировать его:

   ```python
   register(LoggerObserver())
   register(EmailObserver())
   ```

После этого при каждом вызове `NewsFacade.create_news(...)` будут срабатывать и логирование, и условная рассылка.

---

### Краткая сводка по паттернам в news_service

| Паттерн   | Где используется        | Зачем |
|-----------|-------------------------|--------|
| **Factory** | `NewsFactory.create_news` | Единое место создания объекта `News`; упрощение изменений и тестов. |
| **Facade**  | `NewsFacade`             | Один вход для «создать» и «получить список»; скрывает фабрику и вызов notify. |
| **Observer**| `observers`, `notify`, `LoggerObserver` | Реакция на событие «новость создана» без изменения кода фасада/фабрики; легко добавлять новые действия. |

Вместе они дают чёткое разделение: фабрика создаёт объект, фасад управляет сценарием (создание + уведомление, чтение списка), наблюдатели реагируют на события и расширяют поведение без изменения ядра.