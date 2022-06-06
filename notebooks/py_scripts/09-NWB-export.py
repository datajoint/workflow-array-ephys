# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3.8.11 ('ele')
#     language: python
#     name: python3
# ---

# + [markdown] tags=[]
# # DataJoint U24 - Workflow Array Electrophysiology
# -

# ## Setup
#
# First, let's change directories to find the `dj_local_conf` file.

import os
# change to the upper level folder to detect dj_local_conf.json
if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')
assert os.path.basename(os.getcwd())=='workflow-array-ephys', ("Please move to the "
                                                               + "workflow directory")
# We'll be working with long tables, so we'll make visualization easier with a limit
import datajoint as dj; dj.config['display.limit']=10

# If you haven't already populated the `lab`, `subject`, `session`, `probe`, and `ephys` schemas, please do so now with [04-automate](./04-automate-optional.ipynb). Note: exporting `ephys` data is currently only supported on the `no_curation` schema. 

from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys
from workflow_array_ephys.export import (element_lab_to_nwb_dict, subject_to_nwb, 
                                         session_to_nwb, ecephys_session_to_nwb, 
                                         write_nwb)
from element_interface.dandi import upload_to_dandi

# ## Export to NWB
#
# Several Elements have tools for generating NWB materials. We'll use the following keys for testing these functions:

lab_key={"lab": "LabA"}
protocol_key={"protocol": "ProtA"}
project_key={"project": "ProjA"}
session_key={"subject": "subject5",
             "session_datetime": "2018-07-03 20:32:28"}

# To skip ahead, use any of the following links:
# - [Element Lab](#Element-Lab)
# - [Element Animal](#Element-Animal)
# - [Element Session](#Element-Session)
# - [Element Array Electrophysiology](#Element-Array-Electrophysiology) - If you are using all upstream Elements, you can skip to this
# - [Element Interface for DANDI Upload](#DANDI-Upload)

# ### Element Lab <a id='Element-Lab'></a>
#
# Because an NWB file must include session information, `element_lab_to_nwb_dict` can only help package information from the Lab schema into `dict` format. This would be helpful for a team using Element Lab, but not others. 

help(element_lab_to_nwb_dict)

element_lab_to_nwb_dict(lab_key=lab_key, protocol_key=protocol_key, 
                        project_key=project_key)

# ### Element Animal <a id='Element-Animal'></a>
#
# `subject_to_nwb` can use a session key to retrieve subject information, and will return an nwb file with a number of sections specified. When packaging into an NWB file, `pynwb` will display a warning regarding timezone information - datetime fields are assumed to be in local time, and will be converted to UTC.

subject_to_nwb(session_key=session_key)

# ### Element Session <a id='Element-Session'></a>
#
# `session_to_nwb` pulls the same information as above, while also including information about session experimenter and session time. The export process provides the same warning about timezone conversion to UTC.
#

session_to_nwb(session_key=session_key)

# ### Element Array Electrophysiology <a id='Element-Array-Electrophysiology'></a>
#
# `ecephys_session_to_nwb` provides a full export mechanism, returning an NWB file with raw data, spikes, and LFP. Optional arguments determine which pieces are exported. For demonstration purposes, we recommend limiting `end_frame`.
#

help(ecephys_session_to_nwb)

nwbfile = ecephys_session_to_nwb(session_key=session_key,
                                 raw=True,
                                 spikes=True,
                                 lfp="dj",
                                 end_frame=100,
                                 lab_key=lab_key,
                                 project_key=project_key,
                                 protocol_key=protocol_key,
                                 nwbfile_kwargs=None)

nwbfile

# `write_nwb` can then be used to write this file to disk. The following cell will include a timestamp in the filename.

# +
import time
    
write_nwb(nwbfile, f'./temp_nwb/{time.strftime("_test_%Y%m%d-%H%M%S.nwb")}')
# -

# ## DANDI Upload <a id='DANDI-Upload'></a>
#
# `element-interface.dandi` includes the `upload_to_dandi` utility to support direct uploads. For more information, see [DANDI documentation](https://www.dandiarchive.org/handbook/10_using_dandi/).
#
# In order to upload, you'll need...
# 1. A DANDI account
# 2. A `DANDI_API_KEY`
# 3. A `dandiset_id`
#
# These values can be added to your `dj.config` as follows:

dj.config['custom']['dandiset_id']="<six digits as string>" 
dj.config['custom']['dandi.api']="<40-character alphanumeric string>"

# This would facilitate routine updating of your dandiset.

upload_to_dandi(
    data_directory="./temp_nwb/",
    dandiset_id=dj.config['custom']['dandiset_id'],
    staging=True,
    working_directory="./temp_nwb/",
    api_key=dj.config['custom']['dandi.api'],
    sync=False)


