import pandas as pd
import numpy as np
import pylab as p
import sys
import os
import yaml
import time
import math
import random

cwd = os.getcwd()

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", default='', help='/path/to/config.yml')

    args = parser.parse_args()

    if not os.path.exists(args.c):
        print("Configuration File does not exist")
        sys.exit(0)

    #print('sleep for 10 seconds')
    #time.sleep(10)
    #print('run program')
    Optimization(parameters_config=args.c)


class Optimization(object):
    """
    Optimization wrapper object for TOGA test case
    """

    def __init__(self, parameters_config=''):
        self.param_config = self.read_input_params(parameters_config)

        f1, f2 = self.optimize_this_function(self.param_config['gene_list'])
        self.write_metrics(f1, f2)
        if self.param_config['debug'] == True:
            self.test()

    @staticmethod
    def optimize_this_function(gene_list):
        """
        Ideas taken from Prugel-Bennett, "When a genetic algorithm outperforms hill-climbing"
        doi:10.1016/j.tcs.2004.03.038
        
        This function takes a dictionary of genes x0, x1, x2, ..., xN
        The global optimum is assumed to be xi = 1 for all i
        Interpretting the N genes as a binary string of length N, use the Hamming Weight H to define two cost metrics that confuse hill-climbing
        f1: steadily decreases with decreasing H, except for "hurdles" (local minima) at regular intervals
        f2: slow increasing runs with decreasing H, only dropping at regular intervals. While better solutions are found at lower values of H, the local slope generally points to the opposite
        
        Also define two fixed axis functions:
        help: distributes solutions by where in the gene string they perform well, encouraging diversity
        hinder: groups all high-performing solutions, while leaving other partitions open for poor solutions to confuse crossover
        """
        #Compute Hamming distance, H, from all 1 string of genes
        H = 0
        for key in gene_list:
            if not gene_list[key]:
                H += 1
        #print (H)

        # return the index of the group of genes that is most helping the metric
        # toga will ensure spread across this function as a fixed axis, i.e. help with diversity
        def help(gene_list):
            bucketsize = 10
            b = 0
            i = 0
            count = 0
            maxCount = 0
            best = []
            for key in gene_list:
                if gene_list[key]:
                    count += 1
                i += 1
                if i == bucketsize:
                    if count == maxCount:
                        best.append(b)
                    elif count > maxCount:
                        maxCount = count
                        best = [b]
                    b += 1
                    i = 0
                    count = 0
            return best[random.randrange(len(best))] + 0.5
        
        #Only allow strong candidates in a single bucket, keep bad solutions as high performers to confuse crossover
        def hinder(m):
            if m < 98:
                return 0.5
            else:
                return random.randrange(9) + 1.5                

        
        #Metric increasing with i with "hurdles" at every n steps
        #As i decreases with n = 3 e.g.
        #                 X               
        #               X 
        #               
        #           X
        #         X  
        #             X    
        #     X          
        #   X              
        #       X
        # X                      
        def f1(i, n):
            if i == 0:
                return 0
            else:
                return math.ceil(i / float(n)) * n + (i % n) - n + 1
        
        #Similar to f1 but have runs of length n-1, e.g. (n = 4)
        #                 X
        #           X    
        #             X  
        #               X
        #         X  
        #   X            
        #     X          
        #       X       
        # X                
        def f2(i, n):
            return math.ceil(i / float(n)) * n - (i % n)

        return help(gene_list), f1(H, 3)

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

    @staticmethod
    def plot(f2, f3):
        """

        Plot the points being tested

        :return:
        """
        # Create test plots
        p.close('all')
        p.imshow(f2, cmap='afmhot', extent=[0, 10, 0, 10])
        p.colorbar()
        p.title('F2')
        p.xlabel('X')
        p.ylabel('Y')
        p.savefig('test_hamming2.png', dpi=300)

        p.close('all')
        p.imshow(f3, cmap='afmhot', extent=[0, 10, 0, 10])
        p.xlabel('X')
        p.ylabel('Y')
        p.colorbar()
        p.title('F3')
        p.savefig('test_hamming3.png', dpi=300)

        p.close('all')
        p.plot(f2.flatten(), f3.flatten(), '.b', markersize=0.1)
        p.xlabel('F2')
        p.ylabel('F3')
        p.title('F2 vs. F3 for all x,y')
        p.savefig(os.path.join(cwd, 'test_tradeoff.png'), dpi=300)

if __name__ == "__main__":
    main()
