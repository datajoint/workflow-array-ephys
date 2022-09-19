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

# + [markdown] pycharm={"name": "#%% md\n"}
# # Run workflow in an automatic way
#
# In the previous notebook [03-process](03-process.ipynb), we ran through the workflow in detailed steps. For daily running routines, the current notebook provides a more succinct and automatic approach to run through the pipeline using some utility functions in the workflow.
# -

import os
if os.path.basename(os.getcwd()) == "notebooks": os.chdir("..")

import numpy as np
from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

# ## Ingestion of subjects, sessions, probes, probe insertions
#
# 1. Fill subject and session information in files `/user_data/subjects.csv` and `/user_data/sessions.csv`
# 2. Run automatic scripts prepared in `workflow_array_ephys.ingest` for ingestion

from workflow_array_ephys.ingest import ingest_subjects, ingest_sessions

# ##### Insert new entries for subject.Subject from the `subjects.csv` file

ingest_subjects()

# ##### Insert new entries for session.Session, session.SessionDirectory, probe.Probe, ephys.ProbeInsertions from the `sessions.csv` file

ingest_sessions()

# ## [Optional] Insert new ClusteringParamSet for Kilosort
#
# This is not needed if keep using the existing ClusteringParamSet

# + jupyter={"outputs_hidden": false} pycharm={"name": "#%%\n"}
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
# -

# ## Trigger autoprocessing of the remaining ephys pipeline

# First, we'll select a session and add a `ProbeInsertion` from file metadata.

session_key = (session.Session & 'subject="subject6"').fetch1("KEY")
ephys.ProbeInsertion.auto_generate_entries(session_key)

# The `process.run()` function in the workflow populates every automated table in the workflow. If a table is dependent on a manual table upstream, it will not get populated until the manual table is inserted.

from workflow_array_ephys import process
process.run()

# ## Insert new ClusteringTask to trigger ingestion of clustering results
#
# To populate the rest of the tables in the workflow, an entry in the `ClusteringTask` needs to be added to trigger the ingestion of the clustering results, with the two pieces of information specified:
# + the `paramset_idx` used for the clustering job
# + the output directory storing the clustering results

ephys.ClusteringTask.insert1(
    dict(
        session_key,
        insertion_number=0,
        paramset_idx=0,
        clustering_output_dir="subject6/session1/towersTask_g0_imec0",
    ),
    skip_duplicates=True,
)

# run populate again for table Clustering
process.run()

# If you're running an `ephys-mode` with curation, you could use the following to populate the `Curation` table
#
# ```python
# key = (ephys.ClusteringTask & session_key).fetch1("KEY")
# ephys.Curation().create1_from_clustering_task(key)
# process.run()
# ```

# ## Summary and next step
#
# + This notebook runs through the workflow in an automatic manner.
#
# + In the next notebook [05-explore](05-explore.ipynb), we will introduce how to query, fetch and visualize the contents we ingested into the tables.
