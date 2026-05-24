import argparse

from lib.broker import connect, publish, setup_topology
from lib.events import trip_accepted, trip_completed, trip_created, user_registered
from lib.settings import Settings

SAMPLES = {
    "trip.created": lambda: trip_created("674a20000000000000000001", "674a10000000000000000001"),
    "trip.accepted": lambda: trip_accepted("674a20000000000000000001", "674a30000000000000000001"),
    "trip.completed": lambda: trip_completed(
        "674a20000000000000000001", "674a10000000000000000000001"
    ),
    "user.registered": lambda: user_registered("674a10000000000000000000002", "client2"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="publish domain event to RabbitMQ")
    parser.add_argument("event_type", choices=SAMPLES.keys())
    args = parser.parse_args()

    settings = Settings()
    event = SAMPLES[args.event_type]()
    conn = connect(settings)
    ch = conn.channel()
    setup_topology(ch, settings.exchange)
    publish(ch, settings, event)
    conn.close()
    print(f"published {event.event_type} id={event.event_id}")


if __name__ == "__main__":
    main()
