
## Installing and Running the Conda Environment
 The `conda` program is an open source package and environment manager commonly used for Python, and operating at the core of the Anaconda Python distribution.  The YAML file(s) in this directory are intended to define `conda` environments suitable for running the python software in this repository.

 While `conda` is typically used for managing Python packages, it is fully capable of installing and maintaining compiled C/C++ libraries.  For example, the `opencv` library is written in C/C++, and is easily installed into a `conda` environment.

### Installing and Updating Conda
The `conda` program comes with any Anaconda installation.  Instructions for installing Anaconda are here: https://docs.anaconda.com/anaconda/install/.  Make sure Anaconda's `bin` directory is on your path before proceeding.

If preferred, Miniconda may be installed instead.  This only installs the `conda` program, which is all that's truly needed to use the environments.  Instructions for installing Miniconda can be found here:  https://conda.io/docs/user-guide/install/index.html.

If `conda` is already installed, but is not up to date, you can update it with the following command:
```bash
$ conda update conda
```

NOTE: on the MLIA machines, conda is already installed, but you'll want to install your own local version so you have full permissions. Otherwise, you will not be able to do things like update conda or pip.

### Creating the Conda Environment
Assuming you have an up-to-date version of anaconda installed, you can install or update the environments with the commands below.

```bash
$ cd $TOGA
$ conda env create -f envs/toga36-env.yml
```

In the above example, the variable `$TOGA` is assumed to point to the root of the TOGA repository.

NOTE: If using conda, the environment will be stored in /home/$USER/.conda/envs/. Using miniconda, your environment will be stored in /home/$USER/miniconda3/envs.
 
### Updating the Conda Environment
If the `toga36-env.yml` file changes for any reason (e.g. adding new packages), the environment may be updated to be consistent with this new YAML file with the following command.

```bash
$ cd $TOGA
$ conda env update -f envs/toga36-env.yml
```

In the above example, the variable `$TOGA` is assumed to point to the MLIA_GFO repo root.

### Usage
With Anaconda's `bin` directory on your path, you can activate the environment by typing `source activate toga36` (the environment's name, `toga36`, is defined at the top of the YAML file).  Once active, only the packages, and respective versions, installed into the environment will be available when running Python.

Exiting the environment is a simple `source deactivate` command at the command-line.

NOTE:  The `activate` script will not work under `tcsh`/`csh` shells.  It will work under `bash`.  This is an active issue with the `conda` community, and will hopefully be resolved soon.

```bash
$ source activate toga36
$ source deactivate
```

### Exporting an Environment

Once created, an environment's definition may be exported to a YAML file again.  This is a way to effectively freeze an environment, and port it around to other machines.  The command to do this:
```bash
$ conda env export > environment.yml
```
This `environment.yml` file will contain all packages that were installed, which will be a superset on those originally provided, as it will include any dependencies needed by the packages specified in `toga36-env.yml`.  It will also contain the exact version of the installed packages, (hopefully) allowing an environment to be perfectly reproduced on another machine.