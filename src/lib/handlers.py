import json
from pathlib import Path
from typing import Any

READ_MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "read_model.json"


def handle_notification(event: dict[str, Any]) -> None:
    etype = event["event_type"]
    payload = event["payload"]
    if etype == "trip.created":
        print(f"[notify] новый заказ {payload['trip_id']} от user {payload['user_id']}")
    elif etype == "trip.accepted":
        print(f"[notify] водитель {payload['driver_id']} принял {payload['trip_id']}")
    elif etype == "trip.completed":
        print(f"[notify] поездка {payload['trip_id']} завершена")
    elif etype == "user.registered":
        print(f"[notify] регистрация {payload['login']}")
    else:
        print(f"[notify] {etype} {payload}")


def _load_read_model() -> dict[str, Any]:
    if not READ_MODEL_PATH.exists():
        return {"active_trips": []}
    return json.loads(READ_MODEL_PATH.read_text(encoding="utf-8"))


def _save_read_model(data: dict[str, Any]) -> None:
    READ_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    READ_MODEL_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def handle_read_model(event: dict[str, Any]) -> None:
    etype = event["event_type"]
    payload = event["payload"]
    data = _load_read_model()
    active: list[dict[str, str]] = data["active_trips"]
    trip_id = payload.get("trip_id")

    if etype == "trip.created":
        active.append(
            {
                "trip_id": trip_id,
                "user_id": payload["user_id"],
                "status": payload["status"],
            }
        )
    elif etype == "trip.accepted":
        for row in active:
            if row["trip_id"] == trip_id:
                row["status"] = "active"
                row["driver_id"] = payload["driver_id"]
    elif etype == "trip.completed":
        data["active_trips"] = [r for r in active if r["trip_id"] != trip_id]
        _save_read_model(data)
        print(f"[readmodel] убран {trip_id}, файл {READ_MODEL_PATH}")
        return

    data["active_trips"] = active
    _save_read_model(data)
    print(f"[readmodel] {etype} -> {len(data['active_trips'])} active")


def handle_cache(event: dict[str, Any]) -> None:
    print(f"[cache] invalidate trips:active after {event['event_type']}")
