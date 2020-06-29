import pandas as pd
import numpy as np
import pylab as p
import sys
import os
import yaml
import time
import math
import random

import tempfile
from qd_classification.cli import run_resnet_cifar10_trial

cwd = os.getcwd()

def main():
    print("Calling wrapper")
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", default='', help='/path/to/config.yml')

    args = parser.parse_args()

    if not os.path.exists(args.c):
        print("Configuration File does not exist")
        sys.exit(0)

    Optimization(parameters_config=args.c)


class Optimization(object):
    """
    Optimization wrapper object for TOGA test case
    """

    def __init__(self, parameters_config=''):
        self.param_config = self.read_input_params(parameters_config)

        trial_directory = cwd
        data_directory = '/scratch_lg/owls-dev/schibler/datasets/'
        conv3_depth = self.param_config['conv3_depth']
        conv4_depth = self.param_config['conv4_depth']
        pooling = self.param_config['pooling']
        optimizer = self.param_config['optimizer']
        resnet_version = self.param_config['resnet_version']
        learning_rate = 10 ** (-1 * self.param_config['learning_neg_exponent'])

        p = self.optimize_this_function(trial_directory, data_directory, conv3_depth, conv4_depth, 
            pooling, optimizer, resnet_version, learning_rate)

        print("Computed " + str(p))

        self.write_metrics(0.5, p)
        if self.param_config['debug'] == True:
            self.test()

        print("Wrote metrics")

    @staticmethod
    def optimize_this_function(tdir, ddir, c3d, c4d, p, o, rv, lr):
        """

        """

        best_val_acc = run_resnet_cifar10_trial(
            trial_dir=tdir,
            data_dir=ddir,
            conv3_depth=c3d,
            conv4_depth=c4d,
            pooling=p,
            resnet_version=rv,
            optimizer=o,
            learning_rate=lr,
            epochs=40,
            steps_per_epoch=100,
            batch_size=128,
            executions_per_trial=3)

        print(best_val_acc)

        return best_val_acc

    @staticmethod
    def read_input_params(paramater_config=''):
        """

        Insert YAML config reading code to obtain values for x and y

        :param paramater_config:
        :return:
        """
        with open(paramater_config) as f:
            _config = yaml.safe_load(f)

        return _config

    def write_metrics(self, a, b):
        d = {'fixed-axis': [a], 'metric': [b]}
        df = pd.DataFrame(data=d)

        work_dir = os.path.join(cwd, self.param_config['output'])
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        output = os.path.join(work_dir, self.param_config['metrics'])

        df.to_csv(output, index=False, sep=',', encoding='utf-8')

if __name__ == "__main__":
    main()
