import datetime
import sys
from time import timezone

import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, LinearLocator
from scipy.interpolate import griddata

matplotlib.use('agg')
# from mpl_toolkits.mplot3d import Axes3D DO NOT REMOVE THIS
from mpl_toolkits.mplot3d import Axes3D


if 'mpl_toolkits.mplot3d.axis3d' not in sys.modules:
    print("DO NOT REMOVE IMPORT\nfrom mpl_toolkits.mplot3d import Axes3D")
    sys.exit(-1)


class Plot(object):

    def __init__(self, fitness_metrics, maximize, savedir):
        self.fitness_metrics = fitness_metrics

        self.maximize = maximize
        self.save_dir = savedir

        self.max_tick_count = 40

        self.plot_surface = False
        self.plot_wireframe = False
        self.plot_categorical = True

    def plot(self, generation_num=0, points=None):
        """

        :param generation_num:
        :param points:
        :return:
        banana:

        >>> from toga import _doctest
        >>> import tempfile
        >>> import pickle
        >>> import shutil
        >>> import glob
        >>> from toga.optimization_state.metrics import Metrics
        >>> from toga.optimization_state.paretofrontier import ParetoFrontier
        >>> settings = {'banana': {'fixed_axis': True, 'range': [0, 400], 'partitions': 40, 'index': 0},
        ...             'sinc': {'fixed_axis': False, 'range': [-0.5, 0.5], 'partitions': 10, 'index': 1}
        ...             }
        >>> fitness_metrics = Metrics(input_dictionary=settings).metrics
        >>> temp_dir = tempfile.mkdtemp()
        >>> files = glob.glob(os.path.join(_doctest.repo_abspath(), 'test', 'data', 'serialized_data', '*.yml'))
        >>> pareto_frontier = ParetoFrontier(experiment_dir=temp_dir,maximize=False,
        ...                                  fitness_metrics=fitness_metrics, amount_per_bin=3)
        >>> pareto_frontier.datadict.update_from_previous_run(files=files)
        >>> plotter = Plot(fitness_metrics=fitness_metrics, maximize=True, savedir=temp_dir)
        >>> plotter.plot(generation_num=0, points=pareto_frontier.datadict.get_points())
        Top Performers Per bin:
        plotting 2d graph
        >>> shutil.rmtree(temp_dir)
        """
        if len(self.fitness_metrics) == 2:
            print('plotting 2d graph')
            self.plot2d(generation_num=generation_num, points=points)

        if len(self.fitness_metrics) == 3:
            print('plotting 3d graph')
            self.plot3d(generation_num=generation_num, points=points)

    def plot3d(self, generation_num=0, points=None):
        if self.plot_surface or self.plot_wireframe:
            self.surface_plot(generation_num, points)

        _dict = {}
        for a in points:
            if a[2] is not None:
                if a[0] in _dict:
                    _dict[a[0]].append((a[1], a[2]))
                else:
                    _dict[a[0]] = []

        fig, ax = plt.subplots()

        for key, item in _dict.items():
            if item:
                ax.scatter(*zip(*item), label=key)

        lgd = ax.legend(loc='center right', title="{}".format(self.fitness_metrics[0].name), bbox_to_anchor=(1.3, 0.5))
        ax.set_xticklabels(ax.get_xticklabels())
        plt.title('{} {} with respect to {} for each {}'.format("Maximize" if self.maximize else "Minimize",
                                                                self.fitness_metrics[2].name,
                                                                self.fitness_metrics[1].name,
                                                                self.fitness_metrics[0].name))
        plt.xlabel(self.fitness_metrics[1].name)
        plt.ylabel(self.fitness_metrics[2].name)

        axes = plt.gca()

        axes.set_xlim([self.fitness_metrics[1].axis_range[0], self.fitness_metrics[1].axis_range[1]])
        axes.set_ylim([self.fitness_metrics[2].axis_range[0], self.fitness_metrics[2].axis_range[1]])
        now = datetime.datetime.now()
        _datetime = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
        plt.savefig(os.path.join(self.save_dir, f"{_datetime}.png"),
                    dpi=300,
                    format='png',
                    bbox_extra_artists=(lgd,),
                    bbox_inches='tight')
        plt.clf()

    def plot2d(self, generation_num=0, points=None):
        """

        :param generation_num:
        :param points:
        :return:

        >>> import tempfile
        >>> import shutil
        >>> import _doctest
        >>> import pickle
        >>> from toga.optimization_state.metrics import Metrics

        >>> points = [('0.0', None), ('0.02', None), ('0.04', None), ('0.06', None), ('0.08', None), ('0.1', None),
        ... ('0.12', None), ('0.14', None), ('0.16', None), ('0.18', None), ('0.2', None), ('0.22', None),
        ... ('0.24', None), ('0.27', None), ('0.29', None), ('0.31', None), ('0.33', None), ('0.35', None),
        ... ('0.37', None), ('0.39', None), ('0.41', None), ('0.43', None), ('0.45', 0.0981258189781923),
        ... ('0.47', None), ('0.49', None), ('0.51', None), ('0.53', None), ('0.55', None), ('0.57', None),
        ... ('0.59', 0.34567888057920526), ('0.61', None), ('0.63', None), ('0.65', None), ('0.67', None),
        ... ('0.69', None), ('0.71', None), ('0.73', None), ('0.76', None), ('0.78', None), ('0.8', None),
        ... ('0.82', None), ('0.84', None), ('0.86', 0.5158112457158114), ('0.88', None), ('0.9', None),
        ... ('0.92', None), ('0.94', 0.23100436557486365), ('0.96', 0.445314925253777), ('0.98', None), ('1.0', None)]
        >>> settings = {'banana': {'fixed_axis': True, 'range': [0, 400], 'partitions': 40, 'index': 0},
        ...             'sinc': {'fixed_axis': False, 'range': [-0.5, 0.5], 'partitions': 10, 'index': 1}
        ...             }
        >>> fitness_metrics = Metrics(input_dictionary=settings).metrics

        >>> test_file = os.path.join(_doctest.repo_abspath(), 'test', 'data', 'fitness_metrics.pickle')
        >>> temp_dir = tempfile.mkdtemp()
        >>> Plot(fitness_metrics=fitness_metrics, maximize=True, savedir=temp_dir).plot2d(generation_num=0,
        ...         points=points)
        >>> shutil.rmtree(temp_dir)
        """

        points = [(float(x[0]), x[1]) for x in points]
        plt.scatter(*zip(*points))
        plt.title('{} {} with respect to {}'.format("Maximize" if self.maximize else "Minimize",
                                                    self.fitness_metrics[1].name,
                                                    self.fitness_metrics[0].name))
        plt.xlabel(self.fitness_metrics[0].name)
        plt.ylabel(self.fitness_metrics[1].name)

        x_lim = self.fitness_metrics[0].axis_range
        y_lim = self.fitness_metrics[1].axis_range

        axes = plt.gca()
        axes.set_ylim(tuple(y_lim))

        if len(points) + 1 < self.max_tick_count:
            x_ticks = np.linspace(x_lim[0], x_lim[1], len(points) + 1)
        else:
            x_ticks = np.linspace(x_lim[0], x_lim[1], self.max_tick_count)

        plt.xticks(x_ticks, fontsize=7, rotation=90)
        plt.tight_layout()
        now = datetime.datetime.now()
        _datetime = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
        plt.savefig(os.path.join(self.save_dir, f"{_datetime}.png"))
        plt.clf()

    def surface_plot(self, generation_num=0, points=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        x, y, z = zip(*points)
        u_range = self.fitness_metrics[0].axis_range
        v_range = self.fitness_metrics[1].axis_range

        u = np.linspace(float(min(u_range)), float(max(u_range)), self.fitness_metrics[0].partitions)
        v = np.linspace(float(min(v_range)), float(max(v_range)), self.fitness_metrics[1].partitions)
        X, Y = np.meshgrid(u, v)
        Z = griddata((np.asarray(x), np.asarray(y)), np.asarray(z), (X.T, Y.T), method='cubic')

        ax.set_xlabel(self.fitness_metrics[0].name)
        ax.set_ylabel(self.fitness_metrics[1].name)
        ax.set_zlabel(self.fitness_metrics[2].name)

        ax.set_title('{} {} with respect to {} and {}'.format("Maximize" if self.maximize else "Minimize",
                                                              self.fitness_metrics[2].name,
                                                              self.fitness_metrics[0].name,
                                                              self.fitness_metrics[1].name))

        if self.plot_surface:
            surf = ax.plot_surface(X, Y, Z, alpha=1, cmap=plt.get_cmap('afmhot'), linewidth=0, antialiased=False)

            axis_range = self.fitness_metrics[2].axis_range
            if axis_range:
                ax.set_zlim(min(axis_range), max(axis_range))
            ax.zaxis.set_major_locator(LinearLocator(self.fitness_metrics[2].partitions))
            ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

            # Add a color bar which maps values to colors.
            fig.colorbar(surf, aspect=5)

        if self.plot_wireframe:
            ax.plot_wireframe(X, Y, Z, color='black')
        plt.tight_layout()
        now = datetime.datetime.now()
        _datetime = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
        plt.savefig(os.path.join(self.save_dir, f'{_datetime}.png'))
        plt.clf()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
