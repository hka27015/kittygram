# Kittygram API

## Описание
Backend-приложение для управления котами и их достижениями.

## Технологии
- Python 3.13
- Django REST Framework

## Запуск проекта

1. Клонировать репозиторий:
```bash
git clone https://github.com/hka27015/kittygram.git
```

2. Перейти в папку:
```bash
cd kittygram
```

3. Создать и активировать виртуальное окружение:
```bash
py -3.13 -m venv venv
```
```bash
venv\Scripts\activate
```

4. Установить зависимости из файла:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. Создать .env файл:
```bash
copy .env.example .env
```

6. Применить миграции:
```bash
python manage.py migrate
```

7. Запустить сервер:
```bash
python manage.py runserver
```

---

## Запуск через Docker

Сборка и запуск:
```bash
docker-compose up --build
```

Приложение доступно:
http://127.0.0.1:8000/


## Аутентификация

Получение токена:

POST /auth/jwt/create/

Пример:
{
  "username": "user",
  "password": "password"
}

---

## Документация API
Swagger:
http://127.0.0.1:8000/swagger/

---


## Основные возможности
- CRUD для моделей котов и достижений
- JWT-аутентификация
- Фильтрация, поиск, сортировка
- Пагинация результатов  
- Документация API (Swagger)