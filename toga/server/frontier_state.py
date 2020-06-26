import asyncio
import json
import os
import shutil

import yaml
from aiohttp import web
from aiojobs.aiohttp import get_scheduler

from toga.toga_settings import Settings


class FrontierState(object):

    def __init__(self, pareto_frontier):
        self.settings = Settings()
        self.pareto_frontier = pareto_frontier
        self.data = self.pareto_frontier.datadict.get_dictionary()
        self.history = {}
        self.workers = {}
        self.generation_number = 0

    async def submit_individual(self, request: web.Request) -> web.json_response():
        """

        :param request:
        :return:
        """
        individual = await request.json()
        if individual is not None:
            count = individual.get('trials')
            self.pareto_frontier.datadict.add_trials(count)
            self.pareto_frontier.evaluate_fitness([individual])
            uuid = individual.get('uuid')
            response = {'individual': uuid, 'status': 'successfully stored'}
            return web.json_response(json.dumps(response))
        response = {'Malformed sample was sent, not storing'}
        return web.json_response(json.dumps(response))

    async def get_state(self, request):
        """

        :return:
        """
        return web.json_response(json.dumps(self.pareto_frontier.datadict.get_dictionary()))


if __name__ == '__main__':
    import doctest

    doctest.testmod()
