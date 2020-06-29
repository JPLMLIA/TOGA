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

    #Checks that the number of genes on (set to 1) in `genes` falls within range `valid range`
    #Else, flips the minimum number of genes to fit this range in the following manner:
    #   From the set of genes that could be flipped, indentify those for which a parent has the target value,
    #       i.e. crossover *could* have flipped this gene given a different dice roll
    #   Flip genes from this set, weighting choices by the number of parents with the target value
    #       - only applicable when # of parents > 2, since one parent must have conributed the "bad" gene)
    #   If this subset is not sufficient in number, augment with additional random flips
    #       - should only be necessary in the case of 0 parents, else parents are invalid
    @staticmethod
    def _ensure_valid(genes, valid_range, parents):
        items_on = sum(x == 1 for x in genes.values())
        if items_on > max(valid_range) or items_on < min(valid_range):
            if items_on > max(valid_range):
                flip_num = items_on - max(valid_range)
                flip_to = 0
            else:
                flip_num = min(valid_range) - items_on
                flip_to = 1
            keys = []
            unique_keys = set()
            for p in parents:
                for key, item in p.items():
                    if item == flip_to:
                        if genes[key] != flip_to:
                            keys.append(key)
                            if key not in unique_keys:
                                unique_keys.add(key)
                    
            flip_set = set()
            if len(unique_keys) < flip_num:
                remaining_num = flip_num - len(unique_keys)
                remaining_candidates = list(filter(lambda x: genes[x] != flip_to and x not in unique_keys, genes))                        
                flip_set = unique_keys.union(set(np.random.choice(remaining_candidates, size=remaining_num, replace=False)))
            else:
                while len(flip_set) < flip_num:
                    remaining_num = flip_num - len(flip_set)
                    flip_set = flip_set.union(set(np.random.choice(keys, size=remaining_num, replace=False)))
                    keys = list(filter(lambda x: x not in flip_set, keys))
            for i in flip_set:
                genes[i] = flip_to

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
            BinaryBlockGene._ensure_valid(_dict, valid_range, parents)
            return _dict

        return self.random()

    def random(self):
        """

        :return:
        """
        components = self.dictionary.get('components')
        key_len = len(list(components.keys()))
        for key in components.keys():
            components[key] = np.random.choice(2)
        valid_range = self.dictionary.get('sum_range')
        BinaryBlockGene._ensure_valid(components, valid_range, [])

        return components

    def gaussian_step(self):
        return self.random()

    def gaussian_random(self):
        return self.random()

    def _get_random_component_set(self, amount):
        components = self.dictionary.get('components')
        allowed_range = self.dictionary.get('sum_range')
        keys = list(components.keys())
        key_len = len(keys)
        if key_len < amount or amount < min(allowed_range) or key_len > max(allowed_range):
            raise Exception("Amount specified is larger than block size or outside allowed range")
        ids = np.random.choice(key_len, size=amount, replace=False)
        for i in ids:
            components[keys[i]] = 1
        return components

    def scaled(self):
        """

        :return:
        """
        allowed_range = self.dictionary.get('sum_range')
        _min = min(allowed_range)
        _max = max(allowed_range)
        amount = int(math.ceil(_min + (_max - _min) * self.percentage))
        return self._get_random_component_set(amount)

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
        return self._get_random_component_set(amount)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

