from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    payload: dict[str, Any]

    def routing_key(self) -> str:
        return self.event_type

    def body(self) -> bytes:
        return self.model_dump_json().encode()


def trip_created(trip_id: str, user_id: str) -> DomainEvent:
    return DomainEvent(
        event_type="trip.created",
        payload={"trip_id": trip_id, "user_id": user_id, "status": "pending"},
    )


def trip_accepted(trip_id: str, driver_id: str) -> DomainEvent:
    return DomainEvent(
        event_type="trip.accepted",
        payload={"trip_id": trip_id, "driver_id": driver_id, "status": "active"},
    )


def trip_completed(trip_id: str, user_id: str) -> DomainEvent:
    return DomainEvent(
        event_type="trip.completed",
        payload={"trip_id": trip_id, "user_id": user_id, "status": "completed"},
    )


def user_registered(user_id: str, login: str) -> DomainEvent:
    return DomainEvent(
        event_type="user.registered",
        payload={"user_id": user_id, "login": login},
    )
