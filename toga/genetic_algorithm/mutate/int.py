"""
Author: Shawn Anderson

Date  : 1/23/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import numpy as np
import scipy.stats as stats
from toga.genetic_algorithm.genetype import Mutator
from toga.genetic_algorithm.mutate.genemutate import GeneMutate
from toga.utils import goodness_of_fit


class IntGene(GeneMutate):

    def __init__(self,  dictionary=None, parents=None, mutator=Mutator.Crossover, mutator_params={}):
        self.dictionary = dictionary if dictionary is not None else {}
        self.parents = parents
        self.mutator_params = mutator_params if mutator_params is not None else {}
        self.percentage = self.mutator_params.get('percentage') if self.mutator_params.get(
            'percentage') is not None else 1.0
        self.frequency = self.mutator_params.get('frequency')
        super().__init__(dictionary, parents, mutator)

    def mutate(self):
        return super().mutate()

    def crossover(self):
        """

        :return:

        >>> np.random.seed(0)
        >>> t.parents = [23, 45, 97]
        >>> t.crossover()
        97

        >>> np.random.seed(0)
        >>> t.parents = [-99]
        >>> t.crossover()
        -99

        >>> np.random.seed(0)
        >>> t.parents = [5, 19]
        >>> t.crossover()
        19
        """
        if self.parents:
            value = np.random.choice([x for x in self.parents], size=1, replace=False).tolist()[0]
            return value
        else:
            return self.random()

    def random(self):
        """
        :return: Random results from allowed range


        >>> t.dictionary = {}
        >>> t.random()
        Traceback (most recent call last):
        Exception: Range not defined at IntGene

        >>> t.dictionary = {'range': [-27, 30]}
        >>> results = []
        >>> sample_size = 100000
        >>> alpha = 0.05 * sample_size
        >>> for i in range(sample_size):
        ...     results.append(t.random())
        >>> values = t.dictionary.get('range')
        >>> _bins = np.linspace(min(values), max(values), 25)
        >>> hist, bins = np.histogram(results)
        >>> _min = min(hist)
        >>> _max = max(hist)
        >>> alpha > (_max - _min)
        True

        >>> t.dictionary = {'range': [0, 10]}
        >>> results = []
        >>> sample_size = 100000
        >>> for i in range(sample_size):
        ...     results.append(t.random())
        >>> values = t.dictionary.get('range')
        >>> _bins = np.linspace(min(values), max(values), 25)
        >>> hist, bins = np.histogram(results)
        >>> _min = min(hist)
        >>> _max = max(hist)
        >>> alpha = 0.01 * sample_size
        >>> alpha > (_max - _min)
        True
        """
        values = self.dictionary.get('range')
        if not values:
            raise Exception("Range not defined at {}".format(self.__repr__()))
        low = min(values)
        high = max(values)
        val = np.random.randint(low, high=high)
        return int(val)

    def gaussian_step(self):
        """
        >>> np.random.seed(0)
        >>> t.dictionary = {'range': [-10, 10]}
        >>> t.parents = [5]
        >>> t.gaussian_step()

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
            
            # int() will always round down, bad for [0, 1] range
            #return int(new_var)
            return int(round(new_var))
        else:
            return self.random()

    def gaussian_random(self):
        """

        :return:
        """
        values = self.dictionary.get('range')
        lower, upper = min(values), max(values)
        _range = np.arange(lower, upper)
        mu, sigma = np.mean(_range), 3
        _trunc = stats.truncnorm(
            (lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
        out = _trunc.rvs(1)
        return int(out)

    def scaled(self):
        values = self.dictionary.get('range')
        return int(((max(values) - min(values)) * self.percentage) + min(values))

    def minimum(self):
        values = self.dictionary.get('range')
        return int(min(values))

    def maximum(self):
        values = self.dictionary.get('range')
        return int(max(values))

    def __repr__(self):
        return self.__class__.__name__


if __name__ == '__main__':
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.IGNORE_EXCEPTION_DETAIL,
                    extraglobs={'t': IntGene()})

