"""
Author: Shawn Anderson

Date  : 6/3/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import json

import aiohttp
import asyncio
import logging
import queue
import signal
from concurrent.futures import ProcessPoolExecutor
import threading

from toga.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from toga.toga_settings import Settings
from toga.worker import Worker
from toga import logger

logger.setup_logger()
logger = logging.getLogger(__name__)


def run_worker(individual) -> Worker:
    worker = Worker(individual)
    return worker.run()


class TogaClient(object):

    def __init__(self, loop=None):
        """
        :param loop:
        :param run_config:
        """
        self.settings = Settings()
        self.settings.create_output_directory()
        self.url = f'http://{self.settings.host}:{self.settings.port}'
        self.genetic_algorithm = GeneticAlgorithm()

        # Handle asyncio event loop stuff
        self.executor = ProcessPoolExecutor(max_workers=self.settings.process_pool_size)
        self.tasks = []
        self.loop = loop
        self.loop.add_signal_handler(signal.SIGINT, self.stop)
        self.loop.add_signal_handler(signal.SIGTERM, self.stop)

        # Handle overflow population on executor. This prevents the executor from ever going empty
        # While preventing it from overfilling to the point where we spend too long on sub-optimal population building
        # up in queue
        self.population = queue.Queue(maxsize=self.settings.overfill_executor_limit)

        # Track number of trials run since last high performer
        self.trials = 0
        self.trialLock = threading.Lock()

    def run(self):
        logging.info('Starting tasks, Genetic Algorithm Loop and server heartbeat synchronization')
        self.tasks.append(self.loop.create_task(self.request_server_state()))
        self.tasks.append(self.loop.create_task(self.heartbeat()))

        try:
            self.loop.run_forever()
        except asyncio.CancelledError:
            logging.info('Stopping event loop')
            self.stop()

    def stop(self):
        for task in self.tasks:
            logging.info('Cleaning up open tasks...')
            task.cancel()
        logging.info('done.')

    async def submit_results(self, high_performer: dict) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.put(self.url + "/submit", data=json.dumps(high_performer)) as resp:
                return await resp.json(content_type=None)

    async def synchronize_state(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/get_state", data=None) as resp:
                return await resp.json(content_type=None)

    async def request_server_state(self):
        while True:
            res = await self.synchronize_state()
            global_state = json.loads(res)
            self.genetic_algorithm.pareto_frontier.update_from_local_datadict(global_state)
            logging.info(f'Requesting state update from server at {self.url}')
            print('running')
            await asyncio.sleep(360)

    async def heartbeat(self):
        while True:
            if not self.population.full():
                self.population.put(self.genetic_algorithm.create_individual())
            if not self.population.empty():
                overfill_limit = self.settings.process_pool_size + self.settings.overfill_executor_limit
                if len(list(self.executor._pending_work_items.keys())) < overfill_limit:
                    self.tasks.append(self.loop.create_task(self.run_sample()))
            await asyncio.sleep(0.2)

    async def run_sample(self):
        if not self.population.empty():
            individual = self.population.get()
            result = await self.loop.run_in_executor(self.executor, run_worker, individual)
            try:
                high_performer = self.genetic_algorithm.score_results(result)
                logging.info(f'Completed {result.__repr__}')
                self.trialLock.acquire()
                self.trials += 1
                self.trialLock.release()
                if len(high_performer) > 0:
                    self.trialLock.acquire()
                    high_performer[0]['trials'] = self.trials
                    self.trials = 0
                    self.trialLock.release()
                    res = await self.submit_results(high_performer[0])
                    print(json.loads(res))
                else:
                    logging.info(f'Not Adding individual to performance metrics')
            except Exception as e:
                print(e)
                # print(result.individual.convert_to_dict())
                pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = TogaClient(loop=loop)
    client.run()
