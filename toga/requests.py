import json

import aiohttp


async def static_ws(url: str, message=None) -> aiohttp.ClientResponse:
    if message is None:
        message = {}
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url + "/ws") as ws:
            await ws.send_json(json.dumps(message))


async def static_post(url: str, name: str, uuid: str, remove=False) -> aiohttp.ClientResponse:
    _dict = {'worker': name, "uuid": uuid, "remove": remove}
    data = json.dumps(_dict)
    async with aiohttp.ClientSession() as session:
        async with session.post(url + "/available", data=data) as resp:
            return await resp.json()


async def request_task(url) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url + "/request") as resp:
            return await resp.json()


async def available(url='', name='', uuid="parent", remove=False) -> aiohttp.ClientResponse:
    _dict = {'worker': name, "uuid": uuid, "remove": remove}
    data = json.dumps(_dict)
    async with aiohttp.ClientSession() as session:
        async with session.post(url + "/available", data=data) as resp:
            return await resp.json()


async def submit_results(url='', local_state={}) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.put(url + "/submit", data=json.dumps(local_state)) as resp:
            return await resp.json()


async def request_state(url='') -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(url + "/best", data=None) as resp:
            return await resp.json()


async def ws(url, message="") -> None:
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url + "/ws") as ws:
            await ws.send_str(message)
