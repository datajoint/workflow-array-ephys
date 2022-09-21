# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
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

# # Allen Institute Ephys Workshop
# September 22, 2022
#
# + In this notebook, we will show how to interact with a database in Python and how export data into a Neurodata Without Borders (NWB) file.
#
# + Other notebooks in this directory describe the process for running the analysis steps in more detail.
#
# + This notebook is meant to be run on CodeBook (`https://codebook.datajoint.io`) which contains example data.
#
# First, some packages we'll use in this notebook...

import datajoint as dj
import numpy as np
from matplotlib import pyplot
import getpass

# ## Configuration

# These steps are taken from [01-configure](01-configure.ipynb). If you've already saved a config file, you can skip to the next section.

# Enter database credentials.  A DataJoint workflow requires a connection to an existing relational database. The connection setup parameters are defined in the `dj.config` python dictionary.

# + tags=[]
username_as_prefix = dj.config["database.user"] + "_ephys_"
dj.config['custom'] = {
    'database.prefix': username_as_prefix,
    'ephys_root_data_dir': [
        "/home/inbox/0.1.0a4/workflow_ephys_data1/",
        "/home/inbox/0.1.0a4/workflow_ephys_data2/",
        "/home/inbox/0.1.0a4/workflow_localization/"
    ],
    "ephys_mode": "no-curation"
}
# -

# Next, we'll use a prompt to securely save your password.

dj.config["database.password"] = getpass.getpass()

# Now to save these credentials.

dj.config.save_global()

# ## Populating the database

# Next, we'll populate these schema using steps from [04-automate](04-automate-optional.ipynb). If your schema are already populated, you can skip this step. For more details on each of these steps, please visit [that notebook](04-automate-optional.ipynb).

# +
from workflow_array_ephys.pipeline import session, ephys # import schemas
from workflow_array_ephys.ingest import ingest_subjects, ingest_sessions # csv loaders

ingest_subjects(subject_csv_path="/home/user_data/subjects.csv")
ingest_sessions(session_csv_path="/home/user_data/sessions.csv")

params_ks = {
    "fs": 30000,
    "fshigh": 150,
    "minfr_goodchannels": 0.1,
    "Th": [10, 4],
    "lam": 10,
    "AUCsplit": 0.9,
    "minFR": 0.02,
    "momentum": [20, 400],
    "sigmaMask": 30,
    "ThPr": 8,
    "spkTh": -6,
    "reorder": 1,
    "nskip": 25,
    "GPU": 1,
    "Nfilt": 1024,
    "nfilt_factor": 4,
    "ntbuff": 64,
    "whiteningRange": 32,
    "nSkipCov": 25,
    "scaleproc": 200,
    "nPCs": 3,
    "useRAM": 0,
}
ephys.ClusteringParamSet.insert_new_params(
    clustering_method="kilosort2",
    paramset_idx=0,
    params=params_ks,
    paramset_desc="Spike sorting using Kilosort2",
)
session_key = (session.Session & 'subject="subject6"').fetch1("KEY")
ephys.ProbeInsertion.auto_generate_entries(session_key)
# -

# Next, we'll trigger the relevant `populate` commands.

populate_settings = {"display_progress": True}
ephys.EphysRecording.populate(**populate_settings)
ephys.LFP.populate(**populate_settings)
ephys.ClusteringTask.insert1(
    dict(
        session_key,
        insertion_number=0,
        paramset_idx=0,
        clustering_output_dir="subject6/session1/towersTask_g0_imec0",
    ),
    skip_duplicates=True,
)
ephys.Clustering.populate(**populate_settings)
ephys.CuratedClustering.populate(**populate_settings)
# ephys.WaveformSet.populate(**populate_settings) # Time-consuming process

# **Notes:** 
# + `ephys.WaveformSet.populate` takes significant time to populate with current CodeBook hardware allocations. The output will not be used directly in this notebook.
# + The `process` script runs through all `populate` commands in order and could be used instead of the commands above. It could be used as follows
# ```python
# from workflow_array_ephys import process; process.run(display_progress=True)
# ```

# ## Exploring the workflow

# ### Import the workflow
#
# The current workflow is composed of multiple database schemas, each of them corresponding to a module within the `workflow_array_ephys.pipeline` file.

from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

# ### Diagrams and table design
#
# We can plot the workflow diagram.  In relational databases, the entities (i.e. rows) in different tables are connected to each other. Visualization of this relationship helps one to write accurate queries. For the array ephys workflow, this connection is as follows:

# + tags=[]
dj.Diagram(lab.Lab) + dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + \
dj.Diagram(probe) + dj.Diagram(ephys)
# -

subject.Subject()

ephys.EphysRecording()

ephys.CuratedClustering.Unit()

# ### Fetch data
#
# Here, we fetch data from the database and generate a raster plot

subset=ephys.CuratedClustering.Unit & 'unit IN ("6","7","9","14","15","17","19")'
subset

# Fetch the spike times from the database for the units above.

units, unit_spiketimes = (subset).fetch("unit", "spike_times")

# Generate the raster plot.

# +
x = np.hstack(unit_spiketimes)
y = np.hstack([np.full_like(s, u) for u, s in zip(units, unit_spiketimes)])

pyplot.plot(x, y, "|")
pyplot.xlabel("Time (s)")
pyplot.ylabel("Unit")
# -

# ### Export to NWB
#
# The Element's `ecephys_session_to_nwb` function provides a full export mechanism, returning an NWB file with raw data, spikes, and LFP. Optional arguments determine which pieces are exported. For demonstration purposes, we recommend limiting `end_frame`.

from workflow_array_ephys.export import ecephys_session_to_nwb, write_nwb

help(ecephys_session_to_nwb)

# Note that a subset of arguments (`lab_key`, `project_key`, and `protocol_key`) take keys from upstream Elements. To populate this information, see [09-NWB-Export](09-NWB-Export.ipynb).
#
# Next, select an experimental session to export.

dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + \
dj.Diagram(probe) + dj.Diagram(ephys)

session_key=dict(subject="subject5",
                 session_datetime="2018-07-03 20:32:28")

# Return the NWBFile object for the selected experimental session.

nwbfile = ecephys_session_to_nwb(session_key=session_key,
                                 raw=True,
                                 spikes=False, # True requires WaveformSet.populate()
                                 lfp="dj",
                                 end_frame=100,
                                 nwbfile_kwargs=None)

nwbfile

# `write_nwb` can then be used to write this file to disk.

# +
import time
nwb_filename = f"/home/{dj.config['database.user']}/"+time.strftime("_test_%Y%m%d-%H%M%S.nwb")

write_nwb(nwbfile, nwb_filename)
# -

# Next, the NWB file can be uploaded to DANDI.  See the [09-NWB-Export](09-NWB-Export.ipynb) notebook for more details.

# ## Summary and next steps
#
# In this notebook we explored how to query and fetch data from the database, and export an experimental ephys session to a NWB file.  Next, please explore more of the features of the DataJoint Elements in the other notebooks.  Once you are ready to begin setting up your pipeline, fork this repository on GitHub and begin adapting it for your projects requirements.
