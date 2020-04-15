"""
Author: Shawn Anderson

Date  : 6/3/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import uuid

import numpy
import yaml

from toga.genetic_algorithm.gene_structure.genetree import GeneTree
from toga.genetic_algorithm.gene_structure.invdividual import Metrics, Individual, Genetics, Lineage
from toga.optimization_state.paretofrontier import ParetoFrontier
from toga.toga_settings import Settings


class Population(object):

    def __init__(self,
                 pareto_frontier=ParetoFrontier):

        self.settings = Settings()
        self.pareto_frontier = pareto_frontier
        self.base_gene = self.settings.gene_template
        self.gene_mutation_scale = self.settings.gene_mutation_scale
        self.gene_mutation_type = self.settings.active_mutators_by_type
        self.optimization_strategy = self.settings.optimization_strategy

        self.population = None

    def create_individual(self, config):

        with open(config, 'r') as f:
            gene = yaml.safe_load(f)
        individual = Individual(uuid=uuid.uuid4().hex)
        individual.genetics, individual.lineage = self.mutate(config=gene)

        _metrics = Metrics(fitness_metrics=self.settings.optimization_metrics, maximize=self.optimization_strategy)
        individual.metrics = _metrics
        return individual

    def get_random_parents(self):
        active = self.pareto_frontier.current_frontier()
        if not active:
            return []
        keys = list(active.keys())
        bins = numpy.random.choice(keys, 2, replace=True)

        parents = []
        for bin in bins:
            parents.append(numpy.random.choice(active[bin], replace=True))

        return parents

    def select_mutator(self):
        scale = self.gene_mutation_scale
        if scale:
            selection = list(scale.keys())
            raw = list(scale.values())
            weights = [float(i) / sum(raw) for i in raw]
            return str(numpy.random.choice(selection, 1, replace=True, p=weights)[0])
        return ""

    @staticmethod
    def load_parents(parents):
        _parents = []
        for parent in parents:
            item = parent.get('genetics')
            if item is not None:
                gene = item.get('gene')
                _parents.append(gene)
        return _parents

    def mutate(self, config):

        parents = self.get_random_parents()
        mutator = self.select_mutator()

        if not parents:
            gene = Genetics(GeneTree(config=config, parents=None, mutator=mutator,
                                     mutator_params={'type_probability': self.gene_mutation_type}).mutate())

            lineage = Lineage(mutator=mutator, parent1=None, parent2=None, generation_num=0)

            return gene, lineage

        parent1 = parents[0]
        parent2 = parents[1]

        _parents = self.load_parents(parents)

        gene = Genetics(gene=GeneTree(config=config, parents=_parents, mutator=mutator,
                                      mutator_params={'type_probability': self.gene_mutation_type}).mutate())

        lineage = Lineage(mutator=mutator,
                          parent1=parent1,
                          parent2=parent2,
                          generation_num=0)

        return gene, lineage


if __name__ == '__main__':
    import doctest
    doctest.testmod()
