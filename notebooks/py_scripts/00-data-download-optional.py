# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py_scripts//py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3.10.4 64-bit ('python3p10')
#     language: python
#     name: python3
# ---

# # Download example data
#
# This workflow will need Ephys data collected from either SpikeGLX or OpenEphys and the output from kilosort2. We provided an example dataset to be downloaded to run through the pipeline. This notebook walks you through the process to download the dataset.

# ## Install djarchive-client

# The example dataset was hosted on djarchive, an AWS storage. We provide a client package to download the data.[djarchive-client](https://github.com/datajoint/djarchive-client), which could be installed with pip:

# + language="bash"
# pip install git+https://github.com/datajoint/djarchive-client.git
# -

# ## Download ephys test datasets using `djarchive-client`

import os
import djarchive_client

client = djarchive_client.client()

# To browse the datasets that are available in djarchive:

list(client.datasets())

# Each of the datasets have different versions associated with the version of workflow package. To browse the revisions:

list(client.revisions())

# To download the dataset, let's prepare a root directory, for example in `/tmp`:

os.mkdir("/tmp/test_data")

# Then run download for a given set and the revision:

client.download(
    "workflow-array-ephys-benchmark",
    target_directory="/tmp/test_data",
    revision="v1",
)

# ## Directory organization
# After downloading, the directory will be organized as follows:

# ```
# /tmp/test_data/
# - subject6
#     - session1
#         - towersTask_g0_imec0
#         - towersTask_g0_t0_nidq.meta
#         - towersTask_g0_t0.nidq.bin
# ```

# We will use this dataset as an example for the rest of the notebooks. If you use for own dataset for the workflow, change the path accordingly.
#
# The example dataset `subject6/session1` is a dataset recorded with SpikeGLX and processed with Kilosort2. The workflow also supports the processing of dataset recorded with OpenEphys.

# ## Next step
# In the [next notebook](01-configure.ipynb), we will set up the configuration file for the workflow.
