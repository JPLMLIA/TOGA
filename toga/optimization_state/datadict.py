"""
Author: Shawn Anderson

Date  : 12/4/19

Brief : Handles the pareto frontier dictionary updates and accessing

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import collections
from collections import Mapping
import copy
import json
import numpy
from operator import add
import os

import yaml


class DataDict(object):
    _FLAG_FIRST = object()

    def __init__(self, fitness_metrics=[], maximize=True, amount_per_bin=1):
        self.fitness_metrics = fitness_metrics
        self.maximize = maximize
        self.amount_per_bin = amount_per_bin
        self.dictionary = self.create_initial()

    def get_dictionary(self):
        """

        :return:
        """

        return self.dictionary

    def update_from_datadict(self, other):
        """

        :param other:
        :return:
        """
        self.deep_update(self.dictionary, other)

    def update_from_population(self, population=[]):
        """

        :param population:
        :return:
        """
        updated_individuals = []

        def update(_dict={}, key_path=[], value=None):
            _sub = _dict
            for index, item in enumerate(key_path):
                if item in _sub:
                    if index == len(key_path) - 1:
                        items = _sub[item]
                        if not items:
                            _sub[item] = [value]
                        else:
                            items.append(value)
                            items.sort(key=lambda x: x['metrics'][key_path[-1]], reverse=self.maximize)
                            _sub[item] = items[:self.amount_per_bin]

                        if any(x['uuid'] == value['uuid'] for x in _sub[item]):
                            updated_individuals.append(value)
                    else:
                        _sub = _sub[item]
            return _dict

        for individual in population:
            if self.has_metrics(individual):
                key_path = self.get_corresponding_bin(individual)
                self.dictionary = update(_dict=self.dictionary, key_path=key_path, value=individual)
        return self.dictionary, updated_individuals

    def has_metrics(self, individual):
        """

        :param individual:
        :return:
        """
        individual_metrics = individual.get('metrics')
        if not individual_metrics:
            return False

        for metrics in self.fitness_metrics:
            if individual_metrics.get(metrics.name) is None:
                return False
        return True

    def update_from_previous_run(self, files):
        """

        :param files:
        :return:
        """
        population = []
        for file in files:
            population.append(yaml.safe_load(open(file)))
        self.update_from_population(population)

    def create_initial(self):
        """
        name, fixed_axis, axis_range, index
        fitness_metrics = [Metric(name='banana', axis_range=[0, 1],index=0, partitions=10),
                           Metric(name='sinc', axis_range=[0,100], index=1, partitions=20),
                           Metric(name='foo', axis_range=[2.5, math.pi], index=2, partitions=20)] <-- last in list is free axis
        datadict = {'banana':
            {0:{'sinc':{
                0: {'foo': []},
                100: {'foo': []}
                }
            },
            1:{'sinc:{
                0: {'foo': []},
                100: {'foo': []}}
                }
            }
        """

        input_arr = copy.deepcopy(self.fitness_metrics)
        if not input_arr:
            raise Exception("No metrics exist\nName metrics inside the Metrics: fitness: section in the run_config yml")

        def helper(dictionary, array):
            _dict = {}

            if not array:
                return dictionary
            _ = array[-1]

            if not _.fixed_axis:
                _dict[_.name] = []
                return helper(_dict, array[:-1])
            else:
                _range = _.axis_range
                partitions = array[-1].partitions
                _dict[_.name] = {round(el, 2): dictionary for el in numpy.linspace(min(_range),
                                                                                   max(_range),
                                                                                   num=partitions)}
                return helper(_dict, array[:-1])
        return json.loads(json.dumps(helper({}, input_arr)))

    def serialize(self, basedir):
        """

        :param basedir:
        :return:
        """
        population = []
        def walk(node, best_dir):
            for key, item in node.items():
                if isinstance(item, dict):
                    walk(item, best_dir)
                else:
                    if item:
                        for i in item:
                            population.append(i)

        walk(self.dictionary, basedir)
        return population

    def deep_update(self, source, overrides):
        """

        :param source:
        :param overrides:
        :return:
        """
        for key, value in overrides.items():
            if isinstance(value, collections.Mapping) and value:
                returned = self.deep_update(source.get(key, {}), value)
                source[key] = returned
            else:
                items = []
                if source.get(key):
                    items = source[key]
                items.extend(overrides[key])
                items = sorted(items, key=lambda x: x['metrics'][key], reverse=self.maximize)
                items = items[:self.amount_per_bin]
                source[key] = items
        return source

    def get_corresponding_bin(self, individual):
        """

        :param individual:
        :return:
        """
        key_path = []

        _dict = self.dictionary
        for metric in self.fitness_metrics:
            _dict = _dict[metric.name]
            key_path.append(metric.name)
            if metric.fixed_axis:
                # get the bins for this value and sort by float if they're stored as strings for some reason
                bins = sorted([float(i) for i in list(_dict.keys())])
                _bin = bins[0]
                for _ in bins:
                    if individual['metrics'][metric.name] > _:
                        _bin = _
                _dict = _dict[str(_bin)]
                key_path.append(str(_bin))
            else:
                return key_path

    def flatten_dict(self, d, join=add, lift=lambda x: x):
        """

        :param d:
        :param join:
        :param lift:
        :return:
        """

        results = []

        def visit(subdict, results, partialKey):
            for k, v in subdict.items():
                k = "{}_._".format(str(k))
                newKey = lift(k) if partialKey == self._FLAG_FIRST else join(partialKey, lift(k))
                if isinstance(v, Mapping):
                    visit(v, results, newKey)
                else:
                    results.append((newKey, v))

        visit(d, results, self._FLAG_FIRST)
        return results

    def get_non_empty_bins(self):
        """

        :return:
        """
        self._FLAG_FIRST = object()
        original = dict(self.flatten_dict(self.dictionary))
        filtered = {k: v for k, v in original.items() if len(v) > 0}
        return filtered

    def get_points(self):
        """

        :return:
        """
        self._FLAG_FIRST = object()
        flattened = self.flatten_dict(self.dictionary)
        print("Top Performers Per bin:")
        points = []
        for key, value in flattened:
            if value:
                # Key appears like beta_._0.0_._gammma_._
                # split will result in ['beta', '0.0', 'gamma', "]
                # since there is always the trailing split character _._ [-2] will result in the expected key
                value = sorted(value, key=lambda x: key.split("_._")[-2], reverse=self.maximize)
                individual = value[0]
                i = individual['metrics'][self.fitness_metrics[-1].name]
            else:
                i = None

            key = key.split('_._')[:-1]
            key.append(i)
            point = key[1::2]
            points.append(tuple(point))
        return points

