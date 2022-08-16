# Подготовка репозитория 

## Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:cianoid/QRkot_spreadsheets.git
```

```
cd QRkot_spreadsheets
```

## Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/MacOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

## Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

## Создать .env-файл по шаблону (незаполненные переменные заполнить!)

```
APP_TITLE=QRKot
APP_DESCRIPTION=Благотворительный фонда поддержки котиков
DATABASE_URL=sqlite+aiosqlite:///./qrkot.db
SECRET=some-secret-key
# Ваш email
EMAIL=
# Данные аутентификации Google API
TYPE=service_account
PROJECT_ID=
PRIVATE_KEY_ID=
PRIVATE_KEY=
CLIENT_EMAIL=
CLIENT_ID=
AUTH_URI=https://accounts.google.com/o/oauth2/auth
TOKEN_URI=https://oauth2.googleapis.com/token
AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
CLIENT_X509_CERT_URL=
SHEETS_API_VERSION=v4
DRIVE_API_VERSION=v3
FILE_LOCALE=ru_RU
```

# Инициализация БД 

## Обновить БД до последней миграции
```
alembic upgrade head
```

**!** При успехе, вы увидите следующее в консоле:
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> d8ba230cd41e, 0001 First
```

## Запустить проект
```
python -m uvicorn app.main:app
```
В случае активной разработки, рекомендуется добавить ключ **--reload** для автоматического перезапуска сервера

**!** При первом запуске, в случае успеха, вы увидите следующее в консоле:
```
INFO:     Started server process [32254]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Если все прошло успешно, то сервер запущен

## Создание супер-пользователей

Запустите скрипт, введите адрес электронной почты и пароль, для создания супер-пользователя

```
python -m app.scripts.createsuperuser
```

# Результат

После запуска будут доступны ресурсы:

* http://127.0.0.1:8000/docs/ - Swagger-документация
* http://127.0.0.1:8000/charity_project/ - эндпоинты по работе с проектами
* http://127.0.0.1:8000/dontaion/ - эндпоинты по работе с инвестированием в проекты
* http://127.0.0.1:8000/google/ - эндпоинт для создания таблицы с отчетом по закрытым проектам
* http://127.0.0.1:8000/users/ - эндпоинты по работе с пользователями
* http://127.0.0.1:8000/auth/ - эндпоинты для регистрации и аутентификации
