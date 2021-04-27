# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: bl_dev
#     language: python
#     name: bl_dev
# ---

# To properly run the array ephys workflow, we need to properly set up the DataJoint configuration. The configuration will be saved in a file called `dj_local_conf.json` on each machine and this notebook walks you through the process.

# # Set up configuration in root directory of this package
#
# As a convention, we set the configuration up in the root directory of the package and always starts importing datajoint and pipeline modules from there.

import os
os.chdir('../..')

pwd

import datajoint as dj

# # Configure database host address and credentials

# Now let's set up the host, user and password in the `dj.config` global variable

dj.config['database.host'] = '{YOUR_HOST}'
dj.config['database.user'] = '{YOUR_USERNAME}'

# The password could be set with `dj.config['database.password'] = '{YOUR_PASSWORD}'`, but please be careful not to push your password to github.

# You should be able to connect to the database at this stage.

dj.conn()

# # Configure the `custom` field in `dj.config` for the Ephys element

# The ephys pipeline is based on the [DataJoint Array Ephys Element](https://github.com/datajoint/element-ephys). Installation of the element into the bl_pipeline requires the following configurations in the field `custom`:

# ## Database prefix
#
# Giving a prefix to schema could help on the configuration of privilege settings. For example, if we set prefix `neuro_`, every schema created with the current workflow will start with `neuro_`, e.g. `neuro_lab`, `neuro_subject`, `neuro_ephys` etc.
#
# The prefix could be configurated as follows in `dj.config`:

dj.config['custom'] = {'database.prefix': 'neuro_'}

# ## Root directory for raw ephys data
#
# + `ephys_root_data_dir` field indicates the root directory for the ephys raw data from SpikeGLX (e.g. `*imec0.ap.bin`, `*imec0.ap.meta`, `*imec0.lf.bin`, `imec0.lf.meta`)
# + In the database, every path for the ephys raw data is relative to this root path. The benefit is that the absolute path could be configured for each machine, and when data transfer happens, we just need to change the root directory in the config file.
# + This path is specific to each machine, as the name of drive mount could be different for each 
# + In the context of the workflow, all the paths saved into the database or saved in the config file need to be in the POSIX standards (Unix/Linux), with `/`. The path conversion for Windows machines is taken care of inside the elements.

dj.config['custom']['ephys_root_data_dir'] = ['/tmp/archive/brody/RATTER/PhysData/Raw/']

# ## Root directory for kilosort 2 processed results
#
# + `clustering_root_data_dir` field indicates the root directory for the ephys raw data from Kilosort2 (e.g. `spikes_clusters.npy`, `spikes_times.npy` etc.)
# + In the database, every path for the kilosort output data is relative to this root path. The benefit is that the absolute path could be configured for each machine, and when data transfer happens, we just need to change the root directory in the config file.
# + It could be the same or different from `ephys_root_data_dir`
# + This path is specific to each machine, and here is an example of the root directory on a linux machine. In brody lab, the raw ephys data are located in the bucket server.

dj.config['custom']['clustering_root_data_dir'] = '/mnt/bucket/labs/brody/RATTER/PhysData/'

# # Save the configuration as a json file

# With the proper configurations, we could save this as a file, either as a local json file, or a global file.

dj.config.save_local()

# ls

# Local configuration file is saved as `dj_local_conf.json` in the root directory of this package `bl_pipeline_python`. Next time if you change your directory to `bl_pipeline_python` before importing datajoint and the pipeline packages, the configurations will get properly loaded.
#
# If saved globally, there will be a hidden configuration file saved in your root directory. The configuration will be loaded no matter where the directory is.

# +
# dj.config.save_global()
