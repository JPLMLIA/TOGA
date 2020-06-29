import numpy

from toga.genetic_algorithm.genetype import Mutator, GeneType
from toga.genetic_algorithm.mutate.binaryblock import BinaryBlockGene
from toga.genetic_algorithm.mutate.bool import BooleanGene
from toga.genetic_algorithm.mutate.float import FloatGene
from toga.genetic_algorithm.mutate.int import IntGene
from toga.genetic_algorithm.mutate.enum import EnumGene


def select_mutator(mutators):
    if mutators:
        selection = list(mutators.keys())
        raw = list(mutators.values())
        weights = [float(i) / sum(raw) for i in raw]
        return str(numpy.random.choice(selection, 1, replace=True, p=weights)[0])
    return ""


def mutate(gene_type: GeneType.IntType, range_config: dict, value, values: list, mutator: Mutator.Crossover,
           mutator_params: dict):
    # TODO: This works but can get cleaned up to be a one liner
    _ = dict
    if gene_type is None:
        _ = value
    if gene_type == 'int':
        frequency = mutator_params.get('int')
        mutator = select_mutator(frequency)
        _ = IntGene(range_config,
                    values,
                    mutator,
                    mutator_params
                    ).mutate()
    if gene_type == 'float':
        frequency = mutator_params.get('float')
        mutator = select_mutator(frequency)
        _ = FloatGene(range_config,
                      values,
                      mutator,
                      mutator_params
                      ).mutate()
    if gene_type == 'bool':
        frequency = mutator_params.get('bool')
        mutator = select_mutator(frequency)
        _ = BooleanGene(range_config,
                        values,
                        mutator,
                        mutator_params
                        ).mutate()
    if gene_type == 'binary_block':
        frequency = mutator_params.get('binary_block')
        mutator = select_mutator(frequency)
        _ = BinaryBlockGene(range_config,
                            values,
                            mutator,
                            mutator_params
                            ).mutate()
    if gene_type == 'enum':   
        frequency = mutator_params.get('enum')
        mutator = select_mutator(frequency)
        _ = EnumGene(range_config,
                     values,
                     mutator,
                     mutator_params
                     ).mutate()
                     
    return _
