# Сервис такси — ДЗ №6 (Event-Driven)

Вариант: заказ поездок. RabbitMQ, topic exchange, демо producer/consumer, CQRS read-проекция.

## Файлы

| Файл | назначение |
|------|------------|
| `event_driven_design.md` | архитектура, команды/события, CQRS, брокер |
| `event_catalog.md` | каталог событий |
| `docker-compose.yml` | RabbitMQ |
| `src/bin/producer.py` | публикация событий |
| `src/bin/consumer.py` | обработка событий |

## Запуск RabbitMQ

```bash
cp .env.example .env
docker compose up -d
```

Management UI: http://localhost:15672 (guest / guest)

## Producer / Consumer

```bash
cd src
poetry install --no-root
```

Терминал 1 — уведомления:

```bash
poetry run python -m bin.consumer notifications
```

Терминал 2 — read model (CQRS):

```bash
poetry run python -m bin.consumer readmodel
```

Терминал 3 — публикация:

```bash
poetry run python -m bin.producer trip.created
poetry run python -m bin.producer trip.accepted
poetry run python -m bin.producer trip.completed
```

После цепочки `created` → `accepted` → `completed` в `data/read_model.json` остаётся пустой список активных поездок.

Другие события:

```bash
poetry run python -m bin.producer user.registered
```

Инвалидация кеша (как в ДЗ №5):

```bash
poetry run python -m bin.consumer cache
```

## Линтер

```bash
cd src && poetry run ruff check .
```
