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
import threading

import string
import random

import yaml

class DataDict(object):
    _FLAG_FIRST = object()

    def __init__(self, fitness_metrics=[], maximize=True, amount_per_bin=1, history_log=""):
        self.fitness_metrics = fitness_metrics
        self.maximize = maximize
        self.amount_per_bin = amount_per_bin
        self.dictionary = self.create_initial()
        self.trial_count = 0
        self.trial_count_lock = threading.Lock()
        self.track_history = history_log is not None and len(history_log) > 0
        self.history_log = history_log

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

    def add_trials(self, trials):
        self.trial_count_lock.acquire()
        self.trial_count += trials
        self.trial_count_lock.release()

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

        if self.track_history and len(updated_individuals) > 0:
            for new_item in updated_individuals:
                with open(self.history_log, "a") as f:
                    f.write(str(self.trial_count) + ": " + str(new_item['metrics']) + "\n")

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

    def flatten_dict(self, d):
        """

        :param d:
        :param join:
        :param lift:
        :return:
        """
        results = []

        def visit(subdict, results, partialKey):
            for k, v in subdict.items():
                newKey = partialKey + (k,)
                if isinstance(v, Mapping):
                    visit(v, results, newKey)
                else:
                    results.append((newKey, v))   
                             
        empty_key = ()
        visit(d, results, empty_key)
        return results

    def get_non_empty_bins(self):
        """

        :return:
        """
        self._FLAG_FIRST = object()
        original = dict(self.flatten_dict(self.dictionary))
        filtered = {k: v for k, v in original.items() if len(v) > 0}
        return filtered

    def _get_best_metric(self, trials):
        trials = sorted(trials, key=lambda x : x['metrics'][self.fitness_metrics[-1].name], reverse=self.maximize)
        best = trials[0]
        return best['metrics'][self.fitness_metrics[-1].name]

    def get_points(self):
        """

        :return:
        """
        self._FLAG_FIRST = object()
        flattened = self.flatten_dict(self.dictionary)
        points = []
        for key, trials in flattened:
            if trials:
                i = self._get_best_metric(trials)
            else:
                i = None
            points.append((key[-2], i))
        return points

