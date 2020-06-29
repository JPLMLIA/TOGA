import numpy as np
from toga.genetic_algorithm.genetype import Mutator
from toga.genetic_algorithm.mutate.genemutate import GeneMutate


class EnumGene(GeneMutate):

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
        if self.parents:
            return np.random.choice([x for x in self.parents], size=1, replace=False).tolist()[0]       
        else:
            return self.random()

    def random(self):
        values = self.dictionary.get('values')
        i = np.random.choice(len(values), size=1).tolist()[0]
        return values[i]

    def gaussian_step(self):
        return self.random()

    def gaussian_random(self):
        return self.random()

    def scaled(self):
        return self.random()

    def minimum(self):
        values = self.dictionary.get('values')
        return values[0]

    def maximum(self):
        values = self.dictionary.get('values')
        return values[-1]


if __name__ == '__main__':
    import doctest
    
    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
