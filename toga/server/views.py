"""
Author: Shawn Anderson

Date  : 6/3/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""

import json

from aiohttp import web

from toga.optimization_state.paretofrontier import ParetoFrontier


class Handler(object):
    def __init__(self, pareto_frontier=ParetoFrontier):
        self.pareto_frontier = pareto_frontier
        self.data = self.pareto_frontier.datadict.get_dictionary()
        self.history = {}
        self.workers = {}

    async def submit_individual(self, request: web.Request) -> web.json_response():
        res = await request.json()
        data = res.get('data')
        if data is not None:
            high_perfomers = self.pareto_frontier.evaluate_fitness(data)
            print(high_perfomers)
            self.data = self.pareto_frontier.datadict.get_dictionary

    async def submit(self, request: web.Request) -> web.json_response():
        res = await request.json()
        data = res.get('data')
        generation_num = res.get('generation')
        if data is not None:
            if self.data is None:
                self.pareto_frontier.datadict.update_from_datadict(data)
                self.data = self.pareto_frontier.datadict.get_dictionary()
            else:
                self.pareto_frontier.update_from_local_datadict(data)
                self.pareto_frontier.serialize()
            self.pareto_frontier.plot(generation_num=generation_num)

        return web.json_response(json.dumps(self.data))

    async def update_best(self, request: web.Request) -> web.json_response():
        return web.json_response(json.dumps(self.data))
