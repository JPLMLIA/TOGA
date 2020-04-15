import abc

from toga.genetic_algorithm.genetype import Mutator


class GeneMutate(metaclass=abc.ABCMeta):

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

    def __repr__(self):
        return self.__class__.__name__

