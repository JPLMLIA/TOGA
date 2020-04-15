import logging
import os
import pathlib
import platform

import yaml
from toga.singleton import Singleton


class Settings(metaclass=Singleton):
    def __init__(self):

        logging.info('Initializing Settings singleton')

        ga_settings_path = os.path.join(os.path.dirname(__file__), 'config', 'genetic_algorithm_settings.yml')
        with open(os.path.join(ga_settings_path), 'r') as f:
            genetic_algorithm_settings = yaml.safe_load(f)

        assert(genetic_algorithm_settings is not None)

        # settings for how to affect genes and store high performers
        self.gene_mutation_scale = genetic_algorithm_settings['mutators']['scale']
        self.active_mutators_by_type = genetic_algorithm_settings['mutators']['type']
        self.optimization_strategy = genetic_algorithm_settings['optimization_strategy_maximize']
        self.individual_per_bin = genetic_algorithm_settings['individuals_per_bin']

        with open(os.path.join(os.path.dirname(__file__), 'config', 'gene_performance_metrics.yml'), 'r') as f:
            gene_performance_metrics = yaml.safe_load(f)

        assert(gene_performance_metrics is not None)

        # metrics that are used to optimize parameters
        self.optimization_metrics = gene_performance_metrics['fitness']

        with open(os.path.join(os.path.dirname(__file__), 'config', 'server_settings.yml'), 'r') as f:
            server_settings = yaml.safe_load(f)

        assert(server_settings is not None)

        # server settings
        self.host = server_settings['host']
        self.port = server_settings['port']

        with open(os.path.join(os.path.dirname(__file__), 'config', 'run_settings.yml'), 'r') as f:
            run_settings = yaml.safe_load(f)

        assert(run_settings is not None)

        # necessary inputs for TOGA to run
        self.metrics_out_location = run_settings['metrics_location']
        self.gene_template = run_settings['gene_template']
        assert(os.path.exists(self.gene_template))

        # output directory for TOGA files
        self.output_dir = run_settings['work_dir']['base_dir']

        # Settings used to make a runnable command for toga gene testing
        # source activate /anaconda3/etc/profile.d/conda.sh; conda activate helm36;
        #       toga_wrapper --tracker_config /path/to/toga_generated/config.yml
        self.use_conda_env = run_settings['environment']['conda']['use']
        self.environ_name = run_settings['environment']['conda']['environment_name']
        self.conda_shell_exec_loc = run_settings['environment']['conda_shell_executable_location']
        if platform.system() == 'Darwin':
            assert (os.path.exists(self.conda_shell_exec_loc))
        self.runnable_cmd = run_settings['command']['cmd']
        self.gene_arg = run_settings['command']['gene_mapping']['key']
        self.static_args = run_settings['command']['static_args']

        # Rules for how to handle running the subprocess from the above command made from the above
        self.process_pool_size = run_settings['workers']['max_workers']
        self.timeout = run_settings['workers']['max_run_time']
        self.overfill_executor_limit = run_settings['workers']['over_fill_executor']

    def create_output_directory(self):
        if not os.path.exists(self.output_dir):
            pathlib.Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            sub_directories = ["best", "graph", "random_config", "workdir", 'generation_log']
            for sub_dir in sub_directories:
                pathlib.Path(os.path.join(self.output_dir, sub_dir)).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    a = Settings()
    b = Settings()

    assert a is b
