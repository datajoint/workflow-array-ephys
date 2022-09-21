# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3.7.9 ('workflow-calcium-imaging')
#     language: python
#     name: python3
# ---

# # Allen Institute Ephys Workshop
# September 22, 2022
# + In this notebook, we will show how to interact with a database in Python and how export data into a Neurodata Without Borders (NWB) file.
#
# + Other notebooks in this directory describe the process for running the analysis steps in more detail.
#
# + This notebook is meant to be run on CodeBook (`https://codebook.datajoint.io`) which contains example data.
#
# + First run the `01-configure` and `04-automate` notebooks to set up your environment and load example data into the database, respectively.

# ## Configuration

import datajoint as dj
import numpy as np
from matplotlib import pyplot

# Enter database credentials.  A DataJoint workflow requires a connection to an existing relational database. The connection setup parameters are defined in the `dj.config` python dictionary.

# + tags=[]
dj.config['custom'] = {'database.prefix': '<username>_allen_ephys_',
                       'ephys_root_data_dir': ["/tmp/test_data/workflow_ephys_data1/",
                                            "/tmp/test_data/workflow_ephys_data2/",
                                            "/tmp/test_data/workflow_localization/", 
                                            "/home/inbox/0.1.0a4/workflow_ephys_data1/",
                                            "/home/inbox/0.1.0a4/workflow_ephys_data2/",
                                            "/home/inbox/0.1.0a4/workflow_localization/"
                                            ]}
# -

# Import the workflow.  The current workflow is composed of multiple database schemas, each of them corresponding to a module within the `workflow_array_ephys.pipeline` file.

from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

# ## Workflow diagram
#
# Plot the workflow diagram.  In relational databases, the entities (i.e. rows) in different tables are connected to each other. Visualization of this relationship helps one to write accurate queries. For the array ephys workflow, this connection is as follows:

# + tags=[]
dj.Diagram(lab.Lab) + dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + \
dj.Diagram(probe) + dj.Diagram(ephys)
# -

subject.Subject()

ephys.EphysRecording()

ephys.CuratedClustering.Unit()

# ## Fetch data from the database and generate a raster plot

subset=ephys.CuratedClustering.Unit & 'unit IN ("6","7","9","14","15","17","19")'
subset

# Fetch the spike times from the database for the units above.

units, unit_spiketimes = (subset).fetch("unit", "spike_times")

# Generate the raster plot.

# +
x = np.hstack(unit_spiketimes)
y = np.hstack([np.full_like(s, u) for u, s in zip(units, unit_spiketimes)])

pyplot.plot(x, y, "|")
pyplot.set_xlabel("Time (s)")
pyplot.set_ylabel("Unit")
# -

# ## Export to NWB
#
# The Element's `ecephys_session_to_nwb` function provides a full export mechanism, returning an NWB file with raw data, spikes, and LFP. Optional arguments determine which pieces are exported. For demonstration purposes, we recommend limiting `end_frame`.

from workflow_array_ephys.export import ecephys_session_to_nwb, write_nwb

help(ecephys_session_to_nwb)

# Select an experimental session to export.

dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + \
dj.Diagram(probe) + dj.Diagram(ephys)

session_key=dict(subject="subject5",
                 session_datetime="2018-07-03 20:32:28")

# Return the NWBFile object for the selected experimental session.

nwbfile = ecephys_session_to_nwb(session_key=session_key,
                                 raw=True,
                                 spikes=True,
                                 lfp="dj",
                                 end_frame=100,
                                 lab_key=dict(lab='LabA'),
                                 project_key=dict(project='ProjA'),
                                 protocol_key=dict(protocol='ProtA'),
                                 nwbfile_kwargs=None)

nwbfile

# `write_nwb` can then be used to write this file to disk.

# +
import time
nwb_filename = f"/home/{dj.config['database.user']}/"+time.strftime("_test_%Y%m%d-%H%M%S.nwb")

write_nwb(nwbfile, nwb_filename)
# -

# Next, the NWB file can be uploaded to DANDI.  See the `09-NWB-Export` notebook for more details.

# ## Summary and next steps
#
# In this notebook we explored how to query and fetch data from the database, and export an experimental ephys session to a NWB file.  Next, please explore more of the features of the DataJoint Elements in the other notebooks.  Once you are ready to begin setting up your pipeline, fork this repository on GitHub and begin adapting it for your projects requirements.
