# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.9.13 ('ele')
#     language: python
#     name: python3
# ---

# + [markdown] tags=[]
# # DataJoint configuration
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
if os.path.basename(os.getcwd()) == "notebooks": os.chdir("..")
import datajoint as dj

# ## Setup - Credentials
#
# Now let's set up the host, user and password in the `dj.config` global variable

import getpass
dj.config["database.host"] = "{YOUR_HOST}" # CodeBook users should omit this
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
# The prefix could be configurated in `dj.config` as follows. CodeBook users should keep their username as the prefix for schema for declaration permissions.

username_as_prefix = dj.config["database.user"] + "_"
dj.config["custom"] = {"database.prefix": username_as_prefix}

# ### Root directories for raw/processed data
#
# `ephys_root_data_dir` field indicates the root directory for
# + The **ephys raw data** from SpikeGLX or OpenEphys, including `*{.ap,lf}.{bin,meta}`
# + The **clustering results** from kilosort2 (e.g. `spike_{times,clusters}.npy`
#
# The root path typically **do not** contain information of subjects or sessions, all data from subjects/sessions should be subdirectories in the root path.
#
# - In the example dataset downloaded with [these instructions](00-data-download-optional.ipynb), `/tmp/test_data` will be the root. 
# - For CodeBook users, the root is `/home/inbox/0.1.0a4/`
#
# ```
# - subject6
#     - session1
#         - towersTask_g0_imec0
#         - towersTask_g0_t0_nidq.meta
#         - towersTask_g0_t0.nidq.bin
# ```

# If there is only one root path.
dj.config["custom"]["ephys_root_data_dir"] = "/tmp/test_data"
# If there are multiple possible root paths:
dj.config["custom"]["ephys_root_data_dir"] = [
    "/tmp/test_data", 
    "home/inbox/0.1.0a4/workflow_ephys_data1",
    "home/inbox/0.1.0a4/workflow_ephys_data2"
]

dj.config

# + In the database, every path for the ephys raw data is **relative to root path(s)** to allow for the absolute path to be configured for **each machine**. When transferring data, we just need to change the root directory in the config file.
#
# + DataJoint Elements use `pathlib.Path()` to maintain path information in **POSIX standards** (Unix/Linux), with `/`. The path conversion for machines of any operating system is taken care of inside the elements.

# ### Ephys Mode
#
# `element-array-ephys` offers 3 different schemas: `acute`, `chronic`, and `no-curation`. For more information about each, please visit the [electrophysiology description page](https://elements.datajoint.org/description/array_ephys/). This decision should be made before first activating the schema. Note: only `no-curation` is supported for export to NWB directly from the Element.

dj.config["custom"]["ephys_mode"] = "no-curation"  # or acute or chronic

# ## Save configuration
#
# With the proper configurations, we could save this as a file, either as a local json file, or a global file.
#
# Local configuration file is saved as `dj_local_conf.json` in current directory, which is great for project-specific settings.
#
# For first-time and CodeBook users, we recommend saving globally. This will create a hidden configuration file saved in your root directory, loaded whenever there is no local version to override it.

# dj.config.save_local()
dj.config.save_global()

# ## Next Step

# After the configuration, we will be able to review the workflow structure with [02-workflow-structure-optional](02-workflow-structure-optional.ipynb).
