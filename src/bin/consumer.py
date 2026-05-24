import argparse

from lib.broker import consume
from lib.handlers import handle_cache, handle_notification, handle_read_model
from lib.settings import Settings

ROLES = {
    "notifications": ("taxi.notifications", handle_notification),
    "readmodel": ("taxi.readmodel", handle_read_model),
    "cache": ("taxi.cache", handle_cache),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="consume taxi domain events")
    parser.add_argument("role", choices=ROLES.keys(), nargs="?", default="notifications")
    args = parser.parse_args()
    queue, handler = ROLES[args.role]
    consume(Settings(), queue, handler)


if __name__ == "__main__":
    main()
