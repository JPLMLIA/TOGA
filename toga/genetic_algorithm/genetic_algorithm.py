import logging

from aiohttp import web

from toga import logger
from toga.genetic_algorithm.population import Population
from toga.optimization_state.metrics import Metrics
from toga.optimization_state.paretofrontier import ParetoFrontier
from toga.toga_settings import Settings

logger.setup_logger()
logger = logging.getLogger(__name__)


class GeneticAlgorithm(object):

    def __init__(self):
        logging.info('start_time: {start_time}')
        self.settings = Settings()

        self.pareto_frontier = ParetoFrontier(experiment_dir=self.settings.output_dir,
                                              maximize=self.settings.optimization_strategy,
                                              fitness_metrics=Metrics(self.settings.optimization_metrics).metrics,
                                              amount_per_bin=self.settings.individual_per_bin)

        self.population = Population(pareto_frontier=self.pareto_frontier)

    def score_results(self, results):
        individual = results.response()
        logging.info(f'Gene: {individual.uuid} has completed')
        if individual.metrics.metrics_df is not None:
            individual.compose_metrics()

        out = individual.convert_to_dict()
        _metrics = out.get('metrics')
        logging.info(f'{_metrics}')
        high_performer = self.pareto_frontier.evaluate_fitness([out])
        results.cleanup()
        if len(high_performer) > 0:
            logging.info(f'{individual.uuid} was recorded as a high performing individual')
        return high_performer

    def create_individual(self):
        self.population.pareto_frontier = self.pareto_frontier
        return self.population.create_individual(self.settings.gene_template)


if __name__ == '__main__':
    from toga_settings import Settings
    settings = Settings()
    settings.create_output_directory()
    ga = GeneticAlgorithm()
    a = ga.create_individual()
    from toga.worker import Worker
    w = Worker(a)
    out = ga.score_results(w.run())
    print(out)
