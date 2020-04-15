"""
Author: Shawn Anderson

Date  : 1/23/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import abc
import math
import random

import numpy as np
from toga.genetic_algorithm.genetype import Mutator
from toga.genetic_algorithm.mutate.genemutate import GeneMutate


class BinaryBlock(metaclass=abc.ABCMeta):

    def __init__(self, dictionary=None, parents=None, mutator=Mutator):
        self.dictionary = dictionary
        self.parents = parents
        self.mutator = mutator

        _choices = {}
        for name, member in Mutator.__members__.items():
            if hasattr(self, member.value):
                _choices[member.value] = getattr(self, member.value)

        setattr(self, 'choices', _choices)

    @abc.abstractmethod
    def mutate(self):
        if hasattr(self, 'choices'):
            _choices = getattr(self, 'choices')
        return _choices[self.mutator].__get__(self)()

    @abc.abstractmethod
    def crossover(self):
        raise Exception("Method not implemented")

    @abc.abstractmethod
    def random(self):
        raise Exception("Method not implemented")

    @abc.abstractmethod
    def gaussian_step(self):
        raise Exception("Method not implemented")

    @abc.abstractmethod
    def gaussian_random(self):
        raise Exception('Method not implemented')

    @abc.abstractmethod
    def scaled(self):
        raise Exception("Method not implemented")

    @abc.abstractmethod
    def minimum(self):
        raise Exception("Method not implemented")

    @abc.abstractmethod
    def maximum(self):
        raise Exception("Method not implemented")

    def check_parents(self):
        if not self.parents:
            raise Exception("No parents selected")


class BinaryBlockGene(GeneMutate):

    def __init__(self,  dictionary=None, parents=None, mutator=Mutator.Crossover, mutator_params={}):
        self.dictionary = dictionary
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
        """
        parents = [x for x in self.parents]
        if parents:
            _dict = {}
            for key, item in parents[0].items():
                selected_parent = np.random.randint(0, len(parents))
                _dict[key] = parents[selected_parent][key]
            valid_range = self.dictionary.get('sum_range')
            items_on = sum(x == 1 for x in _dict.values())
            if items_on > max(valid_range):
                remove_num = items_on - valid_range
                for i in np.random.choice(list(_dict.keys()), size=remove_num, replace=False):
                    _dict[i] = 0
            return _dict
        return self.dictionary.get('components')

    def random(self):
        """

        :return:
        """
        allowed_range = self.dictionary.get('sum_range')
        amount = random.randint(min(allowed_range), max(allowed_range))
        amount = int(amount)
        components = self.dictionary.get('components')
        key_len = len(list(components.keys()))
        if key_len < amount or key_len < max(allowed_range):
            raise Exception("Amount specified is larger than binary block size")
        selected = np.random.choice(np.asarray(list(components.keys())), size=amount, replace=False)

        for item in selected:
            components[item] = 1
        return components

    def gaussian_step(self):
        return self.random()

    def gaussian_random(self):
        return self.random()

    def scaled(self):
        """

        :return:
        """
        allowed_range = self.dictionary.get('sum_range')
        amount = int(math.ceil(max(allowed_range) * self.percentage))
        components = self.dictionary.get('components')
        key_len = len(list(components.keys()))
        if key_len < amount or key_len < max(allowed_range):
            raise Exception("Amount specified: {} is larger than max allowed binary block size: {}"
                            " or elements in block: {}".format(amount, max(allowed_range), key_len))
        selected = np.random.choice(np.asarray(list(components.keys())), size=amount, replace=False)
        for item in selected:
            components[item] = 1
        return components

    def minimum(self):
        """

        :return:
        """
        components = self.dictionary.get('components')
        return components

    def maximum(self):
        """

        :return:
        """
        allowed_range = self.dictionary.get('sum_range')
        amount = max(allowed_range)
        components = self.dictionary.get('components')
        key_len = len(list(components.keys()))
        if key_len < amount or key_len < max(allowed_range):
            raise Exception("Amount specified is larger than binary block size")
        selected = np.random.choice(np.asarray(list(components.keys())), size=amount, replace=False)
        for item in selected:
            components[item] = 1
        return components


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

