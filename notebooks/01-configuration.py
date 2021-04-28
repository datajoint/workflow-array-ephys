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

# To run the array ephys workflow, we need to properly set up the DataJoint configuration. The configuration will be saved in a file called `dj_local_conf.json` on each machine and this notebook walks you through the process.
#
#
# **The configuration only needs to be set up once**, if you have gone through the configuration before, directly go to [02-process](02-process.ipynb).

# # Set up configuration in root directory of this package
#
# As a convention, we set the configuration up in the root directory of the workflow package and always starts importing datajoint and pipeline modules from there.

import os
os.chdir('..')

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

# The major component of the current workflow is the [DataJoint Array Ephys Element](https://github.com/datajoint/element-ephys). Array Ephys Element requires configurations in the field `custom` in `dj.config`:

# ## Database prefix
#
# Giving a prefix to schema could help on the configuration of privilege settings. For example, if we set prefix `neuro_`, every schema created with the current workflow will start with `neuro_`, e.g. `neuro_lab`, `neuro_subject`, `neuro_ephys` etc.
#
# The prefix could be configurated as follows in `dj.config`:

dj.config['custom'] = {'database.prefix': 'neuro_'}

# ## Root directories for raw ephys data and kilosort 2 processed results
#
# + `ephys_root_data_dir` field indicates the root directory for the **ephys raw data** from SpikeGLX or OpenEphys (e.g. `*imec0.ap.bin`, `*imec0.ap.meta`, `*imec0.lf.bin`, `imec0.lf.meta`) or the **clustering results** from kilosort2 (e.g. `spike_times.npy`, `spike_clusters.npy`). The root path typically **do not** contain information of subjects or sessions, all data from subjects/sessions should be subdirectories in the root path.
# + In the database, every path for the ephys raw data is **relative to this root path**. The benefit is that the absolute path could be configured for each machine, and when data transfer happens, we just need to change the root directory in the config file.
# + The workflow supports **multiple root directories**. If there are multiple possible root directories, specify the `ephys_root_data_dir` as a list.
# + The root path(s) are **specific to each machine**, as the name of drive mount could be different for different operating systems or machines.
# + In the context of the workflow, all the paths saved into the database or saved in the config file need to be in the **POSIX standards** (Unix/Linux), with `/`. The path conversion for machines of any operating system is taken care of inside the elements.

# If using our example dataset downloaded with [this instruction](00-data-download[optional].ipynb), the root directory will be:

# If there is only one root path.
dj.config['custom']['ephys_root_data_dir'] = '/tmp/test_data/workflow-array-ephys-test-set'
# If there are multiple possible root paths:
dj.config['custom']['ephys_root_data_dir'] = ['/tmp/test_data/workflow-array-ephys-test-set']

dj.config

# # Save the configuration as a json file

# With the proper configurations, we could save this as a file, either as a local json file, or a global file.

dj.config.save_local()

# ls

# Local configuration file is saved as `dj_local_conf.json` in the root directory of this package `bl_pipeline_python`. Next time if you change your directory to `bl_pipeline_python` before importing datajoint and the pipeline packages, the configurations will get properly loaded.
#
# If saved globally, there will be a hidden configuration file saved in your root directory. The configuration will be loaded no matter where the directory is.

# +
# dj.config.save_global()
# -

# # Next Step

# After the configuration, we will be able to run through the workflow with [02-process](02-process.ipynb).
