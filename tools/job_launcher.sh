#!/bin/bash
#PBS -N toga
#PBS -J 0-96
#PBS -j eo                                                                      
#PBS -o ///scratch_lg/owls-dev/shawna/pbs_output
#PBS -e //scratch_lg/owls-dev/shawna/pbs_error
#PBS -q array
#PBS -l pmem=1gb                                                                
#PBS -l select=1:ncpus=16

ssh -f -N -L 9119:localhost:9119 shawna@gattaca
source activate toga36
toga-client --source ~/projects/TOGA/test/real_examples/helm_toga_run_config.yml