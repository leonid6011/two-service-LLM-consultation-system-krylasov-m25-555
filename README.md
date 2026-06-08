# Двухсервисная система LLM-консультаций

## Описание

В рамках проекта разрабатывается распределённая система, состоящая из двух логически и технически независимых сервисов, каждый из которых выполняет строго определённую роль. Архитектура построена по принципу разделения ответственности: один сервис отвечает исключительно за аутентификацию и выпуск токенов, второй — за предоставление функциональности LLM-консультаций через Telegram-бота. Такое разделение позволяет изолировать чувствительную логику работы с пользователями и учетными данными от прикладного сервиса, работающего с внешними пользователями и внешними API.

Ключевая идея проекта заключается в том, что Telegram-бот не знает ничего о пользователях, паролях и механизмах регистрации. Он доверяет только корректно подписанному и не истёкшему JWT-токену, выданному специализированным сервисом авторизации. Это приближает архитектуру проекта к реальным микросервисным системам и демонстрирует принципы построения безопасных распределённых приложений.

## Требования

- Python 3.11+
- uv
- RabbitMQ
- Redis

### Установка RabbitMQ и Redis (Ubuntu)

```bash
sudo apt install rabbitmq-server redis-server -y
sudo systemctl start rabbitmq-server redis
sudo rabbitmq-plugins enable rabbitmq_management
```

## Установка и запуск через uv

1. Установите uv
**Linux(Ubuntu)/MacOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh 
source ~/.bashrc
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/leonid6011/two-service-LLM-consultation-system-krylasov-m25-555
cd two-service-LLM-consultation-system-krylasov-m25-555
```

## Запуск

### Auth Service

```bash
cd auth_service
uv venv && source .venv/bin/activate
uv pip install -e .
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI: http://localhost:8000/docs

### Bot Service

Заполнить `bot_service/.env`:
```env
BOT_TOKEN=токен_от_BotFather
JWT_SECRET=change_me_super_secret   # должен совпадать с auth_service/.env
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
OPENROUTER_API_KEY=апи_ключ
OPENROUTER_MODEL=openrouter/auto
```

```bash
cd bot_service
uv venv && source .venv/bin/activate
uv pip install -e .

# терминал 1 для Celery worker
uv run celery -A app.infra.celery_app worker --include=app.tasks.llm_tasks --loglevel=info

# терминал 2 для Bot Service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001

```

## Тестирование

```bash
# Auth Service
cd auth_service
uv run pytest tests/ -v

# Bot Service
cd bot_service
uv run pytest tests/ -v
```
## Демонстрация работы эндпоинтов

1. Регистрация пользователя - POST /auth/register
email: `student_krylasov@email.com`

![register](docs/register.png)

2. Логин и получение JWT - POST /auth/login

![login](docs/login.png)

3. Профиль - GET /auth/me

![me](docs/me.png)

4. Повторная регистрация (409 Conflict)

![negative_register](docs/negative_register.png)

5. Неверный пароль (401 Unauthorized)

![negative_login](docs/negative_login.png)

6. Запрос без токена (401 Unauthorized)

![negative_me](docs/negative_me.png)

7. Тесты Auth Service 12/12 PASSED

![test1](docs/test1.png)

8. Тесты Bot Service 10/10 PASSED

![test2](docs/test2.png)

9. Telegram-бот

![telegram](docs/telegram.png)

10. RabbitMQ

![rabbit](docs/rabbit.png)

## Структура проекта
```
├── auth_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── exceptions.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── user.py
│   │   ├── repositories/
│   │   │   └── users.py
│   │   ├── usecases/
│   │   │   └── auth.py
│   │   └── api/
│   │       ├── deps.py
│   │       ├── router.py
│   │       └── routes_auth.py
│   ├── tests/
│   │   ├── unit/
│   │   │   └── test_security.py
│   │   └── integration/
│   │       └── test_auth_routes.py
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .env
│
└── bot_service/
    ├── app/
    │   ├── main.py
    │   ├── core/
    │   │   ├── config.py
    │   │   └── jwt.py
    │   ├── infra/
    │   │   ├── redis.py
    │   │   └── celery_app.py
    │   ├── tasks/
    │   │   └── llm_tasks.py
    │   ├── services/
    │   │   ├── llm_client.py
    │   │   └── openrouter_client.py
    │   └── bot/
    │       ├── bot.py
    │       ├── dispatcher.py
    │       └── handlers.py
    ├── tests/
    ├── pyproject.toml
    ├── pytest.ini
    └── .env
```
