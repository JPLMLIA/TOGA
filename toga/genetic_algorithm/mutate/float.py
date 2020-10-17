"""
Author: Shawn Anderson

Date  : 1/23/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import numpy as np
import random
from toga.genetic_algorithm.genetype import Mutator
from toga.genetic_algorithm.mutate.genemutate import GeneMutate


class FloatGene(GeneMutate):

    def __init__(self,  dictionary=None, parents=None, mutator=Mutator.Crossover, mutator_params={}):
        self.dictionary = dictionary
        self.parents = parents
        self.mutator_params = mutator_params if mutator_params is not None else {}
        self.percentage = self.mutator_params.get('percentage') if self.mutator_params.get(
            'percentage') is not None else 1.0
        self.frequency = self.mutator_params.get('frequency')
        super().__init__(dictionary, parents, mutator)

    def mutate(self):
        """

        :return:
        """
        return super().mutate()

    def crossover(self):
        """

        :return:
        """

        if self.parents:
            value = np.random.choice([x for x in self.parents], size=1, replace=False).tolist()[0]
            return float(value)
        else:
            return self.random()

    def random(self):
        """

        :return:
        """
        values = self.dictionary.get('range')
        val = np.random.uniform(min(values), max(values))
        return float(val)

    def gaussian_step(self):
        """

        :return:
        """
        if self.parents:
            parent = self.parents[0]
            original = parent
            values = self.dictionary.get('range')

            scale = np.abs((max(values) - min(values)))
            new_var = np.random.normal(loc=original, scale=scale/4)
            new_var = max(min(values), new_var)
            new_var = min(max(values), new_var)
            return float(new_var)
        else:
            return self.random()

    def gaussian_random(self):
        """

        :return:
        """
        values = self.dictionary.get('range')
        dist = np.arange(min(values), max(values))
        return float(min(max(values), max(min(values), random.gauss(np.mean(dist), sigma=3))))

    def scaled(self):
        values = self.dictionary.get('range')
        return float(((max(values) - min(values)) * self.percentage) + min(values))

    def minimum(self):
        values = self.dictionary.get('range')
        return min(values)

    def maximum(self):
        values = self.dictionary.get('range')
        return max(values)


if __name__ == '__main__':
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
