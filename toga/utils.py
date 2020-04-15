"""
Author: Shawn Anderson

Date  : 6/3/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""

import json
import os
from typing import Callable, Optional, Any

import numpy as np
import scipy.stats as stats
import yaml
from sklearn.preprocessing import minmax_scale


def load(file):
    return yaml.safe_load(open(file))


def obtain_configs(config_file):
    try:
        config = yaml.safe_load(open(config_file))
    except:
        if os.path.isfile(config_file):
            raise OSError("Could not open configuration file. Check that file has correct format.")
        else:
            raise OSError("Configuration file not found.")
    return config


def timeit(func: Callable) -> None:
    """

    Magic timeit annotation will get the time before the function is called and the time after it finishes

    :param func: The function pointer of the function that this is annotating
    :return: wrapper
    """
    import time
    get_time = time.time

    outstr = '%s.%s elapsed time: %0.3f seconds'

    def wrapper(*args, **kwargs) -> Callable:
        start_time = get_time()
        res = func(*args, **kwargs)
        print(outstr % (func.__module__, func.__name__, get_time() - start_time))
        return res

    return wrapper


def dict_generator(indict, pre=None) -> Optional[Any]:
    """
    Recursive walk through dictionary and returns a tuple of keypath and value

    Use with a for loop outside this function to return values from the yield params

    :param indict: the dictionary to be traversed in this function
    :param pre: the list of traversals that have already occured
    :return: yield when value is instance of dictionary or yield the pre list
    """
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, pre + [key]):
                    yield d
            else:
                yield (pre + [key], value)
    else:
        yield indict


def first(iterable, default=None):
    for item in iterable:
        return item
    return default


class Decoder(json.JSONDecoder):
    """
    Handle decoding json and preserving numerics as numerics instead of strings
    """

    def decode(self, s) -> Any:

        """
        The decode caller method that returns the private _decode(result)

        :param s: the string to decode
        :return: the value from _decode(result)
        """

        result = super().decode(s)
        return self._decode(result)

    def _decode(self, o) -> Any:
        """
        Tries to match object type to valid python types in this case it supports int dict and lists

        :param o: The object to decode

        :return: The value of the object with the matching type
        """

        if isinstance(o, str):
            try:
                return int(o)
            except ValueError:
                return o
        elif isinstance(o, dict):
            return {k: self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o


def goodness_of_fit(arr: np.ndarray,mean=0.5, sigma=1, min=0, max=1,  dist_type='uniform', alpha=0.05):
    """
    :param num_bins:
        the amount of bins to place the distribution under test into
    :param arr: input array
        type: ndarray expected
    :param dist_type: {'uniform', 'normal'}, optional
        Defines distribution to compare against ).
        Default is 'two-sided'
    :param alpha: level of significance to reject null hypothesis (that arr matches dist_type)
        Default is 0.05
    :return: True if p-value <= level of significance

    >>> np.random.seed(0)
    >>> s = np.random.uniform(-23, 33, 100000)
    >>> goodness_of_fit(s)
    True

    >>> np.random.seed(0)
    >>> s = np.random.uniform(-50.2, 17.9, 1000000)
    >>> goodness_of_fit(s)
    True

    >>> np.random.seed(0)
    >>> s = np.random.uniform(-23, 33, 100000)
    >>> goodness_of_fit(s, alpha=0.95)
    False

    >>> np.random.seed(0)
    >>> s = np.random.normal(loc=0.0, scale=1.0, size=10000)
    >>> goodness_of_fit(s, dist_type='uniform', alpha=0.05)
    False

    >>> np.random.seed(0)
    >>> s = np.random.uniform(-50.2, 17.9, 100000)
    >>> goodness_of_fit(s, dist_type='normal')
    False

    >>> np.random.seed(0)
    >>> x = np.random.normal(0, 1, 100000)
    >>> goodness_of_fit(x, dist_type='normal', alpha=1)
    True

    >>> np.random.seed(0)
    >>> x = np.random.normal(110, 1222, 100000)
    >>> goodness_of_fit(x, dist_type='normal')
    True
    """
    if dist_type == 'uniform':
        # normalize uniform distributions
        arr = minmax_scale(arr, feature_range=(0, 1), copy=True)
        statistic, pvalue = stats.kstest(arr, 'uniform')
        return pvalue > alpha  # reject null hypothesis if alpha is greater than pvalue

    if dist_type == 'normal':
        # using Anderson-Darling test
        # normal/exponential critical values: [15%, 10%, 5%, 2.5%, 1%]

        # sample result: AndersonResult(statistic=1.383562257554786,
        # critical_values=array([0.574, 0.654, 0.785, 0.916, 1.089]),
        # significance_level=array([15. , 10. , 5. , 2.5, 1. ]))
        A2, critical, sig = stats.anderson(arr, dist='norm')

        # [[ True  True  True  True  True]
        #  [ True  True  True  True False]]
        results = np.vstack((np.where((A2 < critical), True, False),
                             np.where((alpha < sig), True, False)))
        # [[ True  True  True  True  True]
        #  [False  True  True  True  True]]
        results = np.flip(results, axis=1)

        transposed_results = results.T
        for column in transposed_results:
            if not column[-1]:
                return column[0]
        # catch the case where alpha is lower than all significance_levels returned from AndersonResult
        # return the 0th column and the associated A2 < critical check at that column
        # this is sorted in reverse (lowest to highest) order from the original critical, sig arrays
        return transposed_results[0][0]


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
