# TOGA
Tuning Optimizing Genetic Algorithm (TOGA)

## Server Build Instructions

```
git clone https://github-fn.jpl.nasa.gov/OWLS/TOGA.git
cd TOGA
conda env create -f envs/toga36-env.yml
source activate toga36
python setup.py develop
```

### Starting a run

###### Starting the toga server
```
In one terminal tab run:
toga-server --source /path/to/this/config.yml

or run in background

nohup toga-server --source /path/to/this/config.yml
```

###### Starting the toga worker client
```
In one terminal tab run:
toga-client --source /path/to/this/config.yml

or run in background

nohup toga-client --source /path/to/this/config.yml
```

##### Starting client on separate host
```
Replace shawna with your ldap account also change the SSH tunnel to the port your testing with

On the machine that you want to run toga on create a SSH tunnel to analysis (assuming server is running there)
ssh -f -N -L 9119:localhost:9119 shawna@analysis

```