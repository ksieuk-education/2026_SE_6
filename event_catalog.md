# Каталог событий — Taxi

Общий envelope для всех событий:

| Поле | Тип | Описание |
|------|-----|----------|
| `event_id` | string (UUID) | идемпотентность, трассировка |
| `event_type` | string | routing key |
| `occurred_at` | datetime (ISO 8601, UTC) | момент факта |
| `version` | int | версия схемы payload |
| `payload` | object | данные события |

---

## user.registered

**Описание:** создан новый пользователь (пассажир).

**Payload:**

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | string | ObjectId / id |
| `login` | string | уникальный логин |

**Producer:** User Service  
**Consumers:** Notification Service (`taxi.notifications`), Analytics Service  
**Доставка:** at-least-once

---

## driver.registered

**Описание:** пользователь зарегистрирован как водитель.

**Payload:**

| Поле | Тип | Описание |
|------|-----|----------|
| `driver_id` | string | id водителя |
| `user_id` | string | id пользователя |

**Producer:** Driver Service  
**Consumers:** Notification Service, Trip Service (опционально)  
**Доставка:** at-least-once

---

## trip.created

**Описание:** создан заказ поездки в статусе `pending`.

**Payload:**

| Поле | Тип | Описание |
|------|-----|----------|
| `trip_id` | string | id поездки |
| `user_id` | string | заказчик |
| `status` | string | `pending` |

**Producer:** Trip Service  
**Consumers:** Notification, Read Model (`taxi.readmodel`), Cache (`taxi.cache`)  
**Доставка:** at-least-once  
**Binding:** `trip.*`

---

## trip.accepted

**Описание:** водитель принял заказ, статус `active`.

**Payload:**

| Поле | Тип | Описание |
|------|-----|----------|
| `trip_id` | string | id поездки |
| `driver_id` | string | id водителя |
| `status` | string | `active` |

**Producer:** Trip Service  
**Consumers:** Notification, Read Model, Cache  
**Доставка:** at-least-once  
**Binding:** `trip.*`

---

## trip.completed

**Описание:** поездка завершена.

**Payload:**

| Поле | Тип | Описание |
|------|-----|----------|
| `trip_id` | string | id поездки |
| `user_id` | string | заказчик |
| `status` | string | `completed` |

**Producer:** Trip Service  
**Consumers:** Notification, Read Model, Analytics, Cache  
**Доставка:** at-least-once  
**Binding:** `trip.#` (read model), `trip.*` (остальные)

---

## Матрица маршрутизации

| event_type | exchange | routing_key | очереди |
|------------|----------|-------------|---------|
| `user.registered` | `taxi.events` | `user.registered` | `taxi.notifications` |
| `driver.registered` | `taxi.events` | `driver.registered` | `taxi.notifications` |
| `trip.created` | `taxi.events` | `trip.created` | notifications, readmodel, cache |
| `trip.accepted` | `taxi.events` | `trip.accepted` | notifications, readmodel, cache |
| `trip.completed` | `taxi.events` | `trip.completed` | notifications, readmodel, cache |
