"""
Author: Lukas Mandrake, Shawn Anderson
Date  : 12/4/19
Brief :
Notes :
Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""

import importlib
import os


def repo_path():
    """
    little function to help resolve location of doctest_files back in repository

    :return: the absolute path to the root of the repository.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repo_relpath(start=None):
    """

    :param start: the current working directory relative to repo root path
    :return: Returns the relative path to the root of the repository.

    >>> test_path = os.path.join(repo_abspath(), 'genetic_algorithm', 'mutate')
    >>> repo_relpath(start=test_path)
    '../..'

     >>> test_path = os.path.join(repo_abspath(), 'genetic_algorithm')
    >>> repo_relpath(start=test_path)
    '..'
    """

    if start is None:
        start = ''
    return os.path.relpath(repo_abspath(), start)


def repo_abspath():
    """

    :return: the absolute path to the directory containing the mlib module.
    """
    toolbox_specs = importlib.util.find_spec('toga')
    return os.path.realpath(os.path.dirname(toolbox_specs.submodule_search_locations[0]))


def module_path():
    return os.path.dirname(os.path.realpath(__file__))


def doctest_input_path():
    """
    :return: the path to the doctest input files
    """
    # return os.path.join(repo_path(), 'tests', 'doctest_input_files')
    return os.path.join(repo_path(), 'tests', 'doctest_files')


def doctest_output_path():
    """

    :return: the path to the doctest output files.
    """
    return os.path.join(repo_path(), 'tests', 'doctest_working')



if __name__ == '__main__':
    import doctest
    doctest.testmod()

    print("repo_path: ", repo_path())
    print("repo_relpath: ", repo_relpath())
    print("repo_abspath: ", repo_abspath())
    print("module_path: ", module_path())
    print("doctest_input_path: ", doctest_input_path())
    print("doctest_output_path: ", doctest_output_path())
