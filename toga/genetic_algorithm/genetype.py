import enum


class Mutator(enum.Enum):
    """
    Defined Mutators
    """
    # global mutators
    Crossover = "crossover"
    GaussianStep = "gaussian_step"
    GaussianRandom = "gaussian_random"
    Random = 'random'
    Scaled = 'scaled'
    minimum = 'minimum'
    maximum = 'maximum'

    # Binary Block specific mutators
    BinaryBlockLeftShift = 'bbleftshift'  # left shift from [1, (N/2)] of length of array
    BinaryBlockRightShift = 'bbrightshift'  # right shift from [1, (N/2)] of length of array
    BinaryBlockXor = 'bbxor'  # crossover logical xor for values
    BinaryBlockAnd = 'bband'  # crossover logical and for values
    BinaryBlockOr = 'bbor'  # crossover logical or for values
    BinaryBlockNotOne = 'bbnotone'  # make 1 value 0 in list that is not
    BinaryBlockNotSome = 'bbnotsome'  # make [1, (N-1)]  store 0
    BinaryBlockNotAll = 'bbnotall'  # make whole list store 0
    BinaryBlockFlipGroup = 'bbflipgroup'  # finds a group of [1, (N/2)] bits and flips them on or off


class GeneType(str, enum.Enum):
    """
    GeneType(param_type, keys)

    These are the supported types when defining a gene_range file that toga looks for and expects
    """

    FloatType = ('float', ['range'])
    IntType = ('int', ['range'])
    BoolType = ('bool', [])
    BinaryBlockType = ('binary_block', ['components', 'sum_range'])

    def __new__(cls, value, keys):
        obj = str.__new__(cls, value)
        obj._value_ = value  # do this to allow looking up by only the param_type
        obj.keys = keys
        return obj


def check_keys(dictionary, gene_type=GeneType.IntType):
    for key in gene_type.keys:
        if key not in dictionary:
            raise Exception("{} not found in gene spec".format(key))
