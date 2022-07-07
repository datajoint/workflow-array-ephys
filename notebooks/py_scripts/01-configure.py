# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: bl_dev
#     language: python
#     name: bl_dev
# ---

# + [markdown] tags=[]
# # DataJoint U24 - Workflow Array Electrophysiology
#
# ## Setup - Working Directory
#
# To run the array ephys workflow, we need to properly set up the DataJoint configuration. The configuration will be saved in a file called `dj_local_conf.json` on each machine and this notebook walks you through the process.
#
# **The configuration only needs to be set up once**, if you have gone through the configuration before, directly go to [02-workflow-structure](02-workflow-structure-optional.ipynb).
#
# As a convention, we set the configuration up in the root directory of the workflow package and always starts importing datajoint and pipeline modules from there.
# -

import os

# change to the upper level folder
if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")
assert os.path.basename(os.getcwd()) == "workflow-array-ephys", (
    "Please move to the " + "workflow directory"
)
import datajoint as dj

# ## Setup - Credentials
#
# Now let's set up the host, user and password in the `dj.config` global variable

import getpass

dj.config["database.host"] = "{YOUR_HOST}"
dj.config["database.user"] = "{YOUR_USERNAME}"
dj.config["database.password"] = getpass.getpass()  # enter the password securily

# You should be able to connect to the database at this stage.

dj.conn()

# ## Setup - `dj.config['custom']`
#
# The major component of the current workflow is the [DataJoint Array Ephys Element](https://github.com/datajoint/element-array-ephys). Array Ephys Element requires configurations in the field `custom` in `dj.config`:

# ### Database prefix
#
# Giving a prefix to schema could help on the configuration of privilege settings. For example, if we set prefix `neuro_`, every schema created with the current workflow will start with `neuro_`, e.g. `neuro_lab`, `neuro_subject`, `neuro_ephys` etc.
#
# The prefix could be configurated as follows in `dj.config`:

dj.config["custom"] = {"database.prefix": "neuro_"}

# ### Root directories for raw/processed data
#
# `ephys_root_data_dir` field indicates the root directory for
# + The **ephys raw data** from SpikeGLX or OpenEphys, including `*{.ap,lf}.{bin,meta}`
# + The **clustering results** from kilosort2 (e.g. `spike_{times,clusters}.npy`
#
# The root path typically **do not** contain information of subjects or sessions, all data from subjects/sessions should be subdirectories in the root path.
#
# In the example dataset downloaded with [these instructions](00-data-download-optional.ipynb), `/tmp/test_data` will be the root
#
# ```
# /tmp/test_data/
# - subject6
#     - session1
#         - towersTask_g0_imec0
#         - towersTask_g0_t0_nidq.meta
#         - towersTask_g0_t0.nidq.bin
# ```

# If there is only one root path.
dj.config["custom"]["ephys_root_data_dir"] = "/tmp/test_data"
# If there are multiple possible root paths:
dj.config["custom"]["ephys_root_data_dir"] = ["/tmp/test_data1", "/tmp/test_data2"]

dj.config

# + In the database, every path for the ephys raw data is **relative to root path(s)**. The benefit is that the absolute path could be configured for each machine, and when data transfer happens, we just need to change the root directory in the config file.
# + The workflow supports **multiple root directories**. If there are multiple possible root directories, specify the `ephys_root_data_dir` as a list.
# + The root path(s) are **specific to each machine**, as the name of drive mount could be different for different operating systems or machines.
# + In the context of the workflow, all the paths saved into the database or saved in the config file need to be in the **POSIX standards** (Unix/Linux), with `/`. The path conversion for machines of any operating system is taken care of inside the elements.

# ### Ephys Mode
#
# `element-array-ephys` offers 3 different schemas: `acute`, `chronic`, and `no-curation`. For more information about each, please visit the [electrophysiology description page](https://elements.datajoint.org/description/array_ephys/). This decision should be made before first activating the schema. Note: only `no-curation` is supported for export to NWB directly from the Element.

dj.config["custom"]["ephys_mode"] = "no-curation"  # or acute or chronic

# ## Save configuration
#
# With the proper configurations, we could save this as a file, either as a local json file, or a global file.

dj.config.save_local()

# ls

# Local configuration file is saved as `dj_local_conf.json` in the root directory of this package `workflow-array-ephys`. Next time if you change your directory to `workflow-array-ephys` before importing datajoint and the pipeline packages, the configurations will get properly loaded.
#
# If saved globally, there will be a hidden configuration file saved in your root directory. The configuration will be loaded no matter where the directory is.

# +
# dj.config.save_global()
# -

# ## Next Step

# After the configuration, we will be able to review the workflow structure with [02-workflow-structure-optional](02-workflow-structure-optional.ipynb).
