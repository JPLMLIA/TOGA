"""
Author: Shawn Anderson

Date  : 1/23/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import numpy as np
from toga.genetic_algorithm.genetype import Mutator
from toga.genetic_algorithm.mutate.genemutate import GeneMutate


class BooleanGene(GeneMutate):

    def __init__(self,  dictionary=None, parents=None, mutator=Mutator.Crossover, mutator_params={}):
        self.dictionary = dictionary
        self.parents = parents
        self.mutator_params = mutator_params if mutator_params is not None else {}
        self.percentage = self.mutator_params.get('percentage') if self.mutator_params.get(
            'percentage') is not None else 1.0
        super().__init__(dictionary, parents, mutator)

    def mutate(self):
        return super().mutate()

    def crossover(self):
        value = np.random.choice([x for x in self.parents], size=1, replace=False).tolist()[0]
        return value

    def random(self):
        return np.random.choice([0, 1],
                                size=1,
                                replace=True).tolist()[0]

    def gaussian_step(self):
        return self.random()

    def gaussian_random(self):
        return self.random()

    def scaled(self):
        return int(np.random.choice([0, 1],
                                    size=1,
                                    replace=True,
                                    p=[1 - self.percentage, self.percentage]).tolist()[0])

    def minimum(self):
        return 0

    def maximum(self):
        return 1


if __name__ == '__main__':
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
