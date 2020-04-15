"""
Author: Shawn Anderson

Date  : 6/3/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""

import os
import platform
import subprocess
from shutil import rmtree
from typing import Tuple, Optional, Any

import pandas as pd
import psutil
import yaml

from toga.toga_settings import Settings


def call(*popenargs, timeout=None, **kwargs):
    """

    Custom implementation of subprocess.call

    As of 12/1/19 subprocess.call is broken in all versions of python with

    Run command with arguments.  Wait for command to complete or
    timeout, then return the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    with subprocess.Popen(*popenargs, **kwargs) as p:
        try:
            return p.wait(timeout=timeout)
        except:  # Including KeyboardInterrupt, wait handled that.
            process = psutil.Process(p.pid)
            for _ in process.children(recursive=True):
                _.kill()
            process.kill()
            raise


class Worker(object):
    """

    Worker object encapsulates the specific gene to be ran with its own attributes needed to run it.

    Overall the procedure worker follows is:

    1.) Store attributes and create a uuid
    2.) Find which config file to map gene to if run_config used to toga allows for multiple configs
    3.) Create temporary directory to run system TOGA is optimzing in and have it output temporary files to
    4.) Serialize gene to yaml file in a temporary location
    5.) Create a run command with modified values
    6.) Run system TOGA is optimizing with the command
    7.) Retrieve metrics as dataframe, the gene used to generate metrics, mutator used to generate gene
    """

    def __init__(self, individual):
        """

        :param gene: The generated gene to be mapped to a runnable config.yml
        :param mutator: The mutator that caused this gene to occur
        :param run_config: The run parameters as a dictionary used by TOGA
        """

        self.settings = Settings()
        self.timeout = self.settings.timeout
        self.experiment_dir = self.settings.output_dir

        self.individual = individual
        self.gene = individual.genetics.gene
        self.mutator = individual.lineage.mutator
        self.generation_num = individual.lineage.generation_num
        self.uuid = individual.uuid

        self.serialization_path = os.path.join(self.experiment_dir, 'random_config',
                                               f'{self.uuid}_{os.path.basename(self.settings.gene_template)}')
        self.relative_work_dir = os.path.join(os.path.join(self.experiment_dir, "workdir"), self.uuid)

    def make_run_command(self) -> str:
        command = ''
        if self.settings.use_conda_env:
            if platform.system() == 'Darwin':
                command += f'source activate {self.settings.conda_shell_exec_loc};' \
                    f'conda activate {self.settings.environ_name};'
            else:
                command += f'source activate {self.settings.environ_name};'

        command += f'{self.settings.runnable_cmd} ' \
            f'{self.settings.gene_arg} {self.serialization_path} {self.settings.static_args}'
        return command

    def run(self):
        """


        :return: self
        """
        if not os.path.exists(self.relative_work_dir):
            os.mkdir(self.relative_work_dir)

        self.serialize_chromosome(
            active_chromosome=self.gene,
            outpath=self.serialization_path)

        cmd = self.make_run_command()
        try:
            call(cmd,
                 shell=True,
                 stderr=subprocess.STDOUT,
                 cwd=self.relative_work_dir,
                 timeout=self.timeout
                 )
        except subprocess.TimeoutExpired:
            return self

        return self

    @staticmethod
    def serialize_chromosome(active_chromosome={}, outpath="") -> None:
        with open(outpath, 'w') as outfile:
            yaml.dump(active_chromosome, outfile)

    def cleanup(self) -> None:
        if os.path.isdir(self.relative_work_dir):
            rmtree(self.relative_work_dir, ignore_errors=True)
        os.remove(self.serialization_path)

    def response(self) -> Tuple[Optional[Any], Optional[Any], Any]:
        metrics_path = os.path.join(self.relative_work_dir, self.settings.metrics_out_location)
        data_frame = None

        if os.path.isfile(metrics_path):
            with open(metrics_path) as f:
                data_frame = pd.read_csv(f)
        else:
            print("Metrics File not found: {}".format(metrics_path))

        self.individual.metrics.metrics_df = data_frame

        return self.individual
