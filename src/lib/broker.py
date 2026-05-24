import json
from collections.abc import Callable
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel

from lib.events import DomainEvent
from lib.settings import Settings

QUEUE_BINDINGS: dict[str, list[str]] = {
    "taxi.notifications": ["trip.*", "user.registered", "driver.registered"],
    "taxi.readmodel": ["trip.#"],
    "taxi.cache": ["trip.*"],
}


def connect(settings: Settings) -> pika.BlockingConnection:
    creds = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_password)
    params = pika.ConnectionParameters(
        host=settings.rabbit_host,
        port=settings.rabbit_port,
        virtual_host=settings.rabbit_vhost,
        credentials=creds,
    )
    return pika.BlockingConnection(params)


def setup_topology(channel: BlockingChannel, exchange: str) -> None:
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    for queue, keys in QUEUE_BINDINGS.items():
        channel.queue_declare(queue=queue, durable=True)
        for key in keys:
            channel.queue_bind(queue=queue, exchange=exchange, routing_key=key)


def publish(channel: BlockingChannel, settings: Settings, event: DomainEvent) -> None:
    channel.basic_publish(
        exchange=settings.exchange,
        routing_key=event.routing_key(),
        body=event.body(),
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
            message_id=event.event_id,
            type=event.event_type,
        ),
        mandatory=True,
    )


def parse_event(body: bytes) -> dict[str, Any]:
    return json.loads(body)


def consume(
    settings: Settings,
    queue: str,
    handler: Callable[[dict[str, Any]], None],
) -> None:
    conn = connect(settings)
    ch = conn.channel()
    setup_topology(ch, settings.exchange)
    ch.basic_qos(prefetch_count=1)

    def on_message(
        channel: BlockingChannel,
        method: pika.spec.Basic.Deliver,
        _props: pika.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            handler(parse_event(body))
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            raise

    ch.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=False)
    print(f"listening {queue} on {settings.exchange}")
    ch.start_consuming()
