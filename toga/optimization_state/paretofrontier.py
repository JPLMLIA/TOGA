"""
Author: Shawn Anderson

Date  : 12/4/19

Brief : Wrapper class around datadict and frontier plots

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""

import glob
import os
import pprint
import shutil

from toga.optimization_state.frontier_plots import Plot
from toga.optimization_state.datadict import DataDict


class ParetoFrontier(object):

    def __init__(self, experiment_dir, maximize, fitness_metrics, amount_per_bin, history_log):
        self.experiment_dir = experiment_dir
        self.maximize = maximize
        self.fitness_metrics = fitness_metrics
        self.amount_per_bin = amount_per_bin
        self.datadict = DataDict(fitness_metrics=self.fitness_metrics,
                                 maximize=self.maximize,
                                 amount_per_bin=self.amount_per_bin,
                                 history_log=history_log)

        self._plot = Plot(self.fitness_metrics,
                          self.maximize,
                          os.path.join(self.experiment_dir, 'graph'))

    def evaluate_fitness(self, population: list):
        reference_dict, new_additions = self.datadict.update_from_population(population)
        return new_additions

    def update_from_local_datadict(self, datadict):
        self.datadict.update_from_datadict(datadict)

    def update_from_previous_run(self):
        best = os.path.join(self.experiment_dir, "best")
        files = glob.glob(os.path.join(best, "*.yml"))
        if files:
            self.datadict.update_from_previous_run(files)

    def serialize(self):
        best = os.path.join(self.experiment_dir, "best")
        self.clear_previous(best)
        population = self.datadict.serialize(best)
        return population

    @staticmethod
    def clear_previous(directory):
        shutil.rmtree(directory)
        os.mkdir(directory)

    def current_frontier(self):
        return self.datadict.get_non_empty_bins()

    def print_bests(self):
        pprint.PrettyPrinter().pprint(self.datadict.get_points())

    def plot(self, generation_num=0):
        print("Top performers per bin at trial {0}...".format(self.datadict.trial_count))
        print(self.datadict.get_points())      
        self._plot.plot(generation_num=generation_num,
                        points=self.datadict.get_points())


if __name__ == '__main__':
    import doctest
    doctest.testmod()
