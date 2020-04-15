import asyncio

from toga.client import TogaClient


def main():
    client = TogaClient(loop=asyncio.get_event_loop())
    client.run()


if __name__ == "__main__":
    main()
