import pandas as pd
import numpy as np
import pylab as p
import sys
import os
import yaml
import time

cwd = os.getcwd()
PI = 3.141592654


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", default='', help='/path/to/config.yml')

    args = parser.parse_args()

    if not os.path.exists(args.c):
        print("Configuration File does not exist")
        sys.exit(0)

    print('sleep for 10 seconds')
    time.sleep(10)
    print('run program')
    Optimization(parameters_config=args.c)


class Optimization(object):
    """
    Optimization wrapper object for TOGA test case
    """

    def __init__(self, parameters_config=''):
        """

        :param x:
        :param y:
        :return:
        """
        self.param_config = self.read_input_params(parameters_config)

        banana, sinc = self.optimize_this_function(self.param_config['x'], self.param_config['y'])
        self.write_metrics(banana, sinc)
        if self.param_config['debug'] == True:
            self.test()

    @staticmethod
    def optimize_this_function(x, y):
        """
        A complex function of both x and y. Returns two values: banana and sinc. These are our "metrics" to trade off against.
        banana has a well known minima at -1.2,1

        :param x: -1.5 to 1.5
        :param y: 0.7 to 2.0

        :return: tuple from both functions values
        """
        banana = (1 - x) ** 2 + 100 * (y - x * x) ** 2
        sinc = np.sin(PI * x) / PI / x * np.sin(PI * y) / PI / y

        return banana, sinc

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

    def write_metrics(self, banana, sinc):
        d = {'banana': [banana], 'sinc': [sinc]}
        df = pd.DataFrame(data=d)

        work_dir = os.path.join(cwd, self.param_config['output'])
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        output = os.path.join(work_dir, self.param_config['metrics'])

        df.to_csv(output, index=False, sep=',', encoding='utf-8')

    @staticmethod
    def plot(banana, sinc):
        """

        Plot the points being tested

        :return:
        """
        # Create test plots
        p.close('all')
        p.imshow(banana, cmap='afmhot', extent=[-1.5, 1.5, 0.7, 2.0])
        p.colorbar()
        p.title('Banana')
        p.xlabel('X')
        p.ylabel('Y')
        p.savefig('test_banana.png', dpi=300)

        p.close('all')
        p.imshow(sinc, cmap='afmhot', extent=[-1.5, 1.5, 0.7, 2.0])
        p.xlabel('X')
        p.ylabel('Y')
        p.colorbar()
        p.title('Sinc')
        p.savefig('test_sinc.png', dpi=300)

        p.close('all')
        p.plot(banana.flatten(), sinc.flatten(), '.b', markersize=0.1)
        p.xlabel('Banana')
        p.ylabel('Sinc')
        p.title('Banana vs. Sinc for all x,y')
        p.savefig(os.path.join(cwd, 'test_tradeoff.png'), dpi=300)

    def test(self):
        """

        :return:
        """
        RESX = 1000
        RESY = 1000

        banana = np.zeros((RESX, RESY))
        sinc = np.zeros((RESX, RESY))

        _x = np.linspace(-1.5, 1.5, RESX)
        _y = np.linspace(0.7, 2.0, RESY)

        # Evaluate for entire vector X for a specific y
        for yi, y in enumerate(_y):
            banana[:, yi], sinc[:, yi] = self.optimize_this_function(_x, y)

        self.plot(banana, sinc)


if __name__ == "__main__":
    main()
