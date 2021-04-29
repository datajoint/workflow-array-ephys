# -*- coding: utf-8 -*-
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
#     display_name: ephys_workflow_runner
#     language: python
#     name: ephys_workflow_runner
# ---

# # Interatively run array ephys workflow

# This notebook walks you through the steps in detail to run the ephys workflow.  
#
# + If you need a more automatic approach to run the workflow, refer to [03-automate](03-automate.ipynb)
# + The workflow requires neuropixels meta file and kilosort output data. If you haven't configure the paths, refer to [01-configuration](01-configuration.ipynb)
# + To overview the schema structures, refer to [02-workflow-structure](02-workflow-structure.ipynb)

# Let's will change the directory to the package root to load configuration and also import relevant schemas.

import os
os.chdir('..')

import datajoint as dj
from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

# ## Ingestion of metadata: subjects, sessions, probes, and probe insertions
#
# The first step to run through the workflow is to insert metadata into the following tables:
#
# + subject.Subject: an animal subject for experiments
# + session.Session: an experimental session performed on an animal subject
# + session.SessionDirectory: directory to the data for a given experimental session
# + probe.Probe: probe information
# + ephys.ProbeInsertion: probe insertion into an animal subject during a given experimental session

dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + dj.Diagram(probe.Probe) + dj.Diagram(ephys.ProbeInsertion)

# Our example dataset is for subject6, session1.

# ### Ingest Subject

subject.Subject.heading

# insert entries with insert1() or insert(), with all required attributes specified in a dictionary
subject.Subject.insert1(
    dict(subject='subject6', sex='M', subject_birth_date='2020-01-04'),
    skip_duplicates=True) # skip_duplicates avoids error when inserting entries with duplicated primary keys
subject.Subject()

# ### Ingest Session

session.Session.describe();

session.Session.heading

session_key = dict(subject='subject6', session_datetime='2021-01-15 00:00:00')
session.Session.insert1(session_key, skip_duplicates=True)
session.Session()

# ### Ingest SessionDirectory

session.SessionDirectory.describe();

session.SessionDirectory.heading

session.SessionDirectory.insert1(
    dict(subject='subject6', session_datetime='2021-01-15 00:00:00',
         session_dir='subject6/session1'),
    skip_duplicates=True)
session.SessionDirectory()

# **Note**:  
#
# the `session_dir` needs to be:
# + a directory **relative to** the `ephys_root_path` in the configuration file, refer to [01-configuration](01-configuration.ipynb) for more information.
# + a directory in POSIX format (Unix/Linux), with `/`, the difference in Operating system will be taken care of by the elements.

# ### Ingest Probe

probe.Probe.heading

probe.Probe.insert1(
    dict(probe='17131311651', probe_type='neuropixels 1.0 - 3B'),
    skip_duplicates=True) # this info could be achieve from neuropixels meta file.
probe.Probe()

# ### Ingest ProbeInsertion

ephys.ProbeInsertion.describe();

ephys.ProbeInsertion.heading

ephys.ProbeInsertion.insert1(
    dict(subject='subject6', session_datetime="2021-01-15 00:00:00",
         insertion_number=0, probe='17131311651'),
    skip_duplicates=True)  # probe, subject, session_datetime needs to follow the restrictions of foreign keys.
ephys.ProbeInsertion()

# ## Automate this manual step
#
# In this workflow, these manual steps could be automated by:
# 1. Insert entries in files `/user_data/subjects.csv` and `/user_data/session.csv`
# 2. Extract user-specified information from `/user_data/subjects.csv` and `/user_data/sessions.csv` and insert to Subject and Session tables by running:
# ```
# from workflow_array_ephys.ingest import ingest_subjects, ingest_sessions
# ingest_subjects()
# ingest_sessions()
# ```
# `ingest_sessions` also extracts probe and probe insertion information automatically from the meta file.
#
# This is the regular routine for daily data processing, illustrated in notebook [04-automate](04-automate.ipynb).

# ## Populate EphysRecording

# Now we are ready to populate EphysRecording, a table for entries of ephys recording in a particular session.

dj.Diagram(session.Session) + \
(dj.Diagram(probe.ElectrodeConfig) + 1) + \
dj.Diagram(ephys.EphysRecording) + dj.Diagram(ephys.EphysRecording.EphysFile) 
# # +1 means plotting 1 more layer of the child tables

# The first argument specify a particular session to populate
ephys.EphysRecording.populate(session_key, display_progress=True)

# Populate EphysRecording extracts the following information from .ap.meta file from SpikeGLX:
#
# 1. **probe_element.EelectrodeConfig**: this procedure detects new ElectrodeConfig, i.e. which 384 electrodes out of the total 960 on the probe were used in this ephys session, and save the results into the table `probe_element.EelectrodeConfig`. Each entry in table `ephys_element.EphysRecording` specifies which ElectrodeConfig is used in a particular ephys session. 

# For this ephys session we just populated, Electrodes 0-383 was used.

probe.ElectrodeConfig()

probe.ElectrodeConfig.Electrode()

# 2. **ephys.EphysRecording**: note here that it refers to a particular electrode_config identified with a hash.

ephys.EphysRecording() & session_key

# 3. **ephys_element.EphysRecording.EphysFile**

ephys.EphysRecording.EphysFile() & session_key

# ## Create ClusteringTask and run/validate Clustering

dj.Diagram(ephys.EphysRecording) + ephys.ClusteringParamSet + ephys.ClusteringTask + \
ephys.Clustering

# The next major table in the ephys pipeline is the `ClusteringTask`.
#
# + In the future release of ephys elements, we will aim to trigger Clustering within the workflow, and register an entry in `ClusteringTask` is a manual step to let the pipeline know that there is a Clustering Task to be processed.
#
# + Currently, we have not supported the processing of Kilosort2 within the workflow. `ClusteringTask` is a place holder
# indicating a Kilosort2 clustering task is finished and the clustering results are ready for processing. 
#
# + The `ClusteringTask` table depends on the table `ClusteringParamSet`, which are the parameters of the clustering task and needed to be inserted first. 

# A method of the class `ClusteringParamSet` called `insert_new_params` helps on the insertion of params_set

# insert clustering task manually
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
    "useRAM": 0
}
ephys.ClusteringParamSet.insert_new_params(
    'kilosort2', 0, 'Spike sorting using Kilosort2', params_ks)
ephys.ClusteringParamSet()

# We are then able to insert an entry into the `ClusteringTask` table. One important field of the table is `clustering_output_dir`, which specifies the Kilosort2 output directory for the later processing.  
# **Note**: this output dir is a relative path to be combined with `clustering_root_directory` in the config file.

ephys.ClusteringTask.describe();

ephys.ClusteringTask.heading

ephys.ClusteringTask.insert1(
    dict(session_key, insertion_number=0, paramset_idx=0,
         clustering_output_dir='subject6/session1/towersTask_g0_imec0'),
    skip_duplicates=True)

ephys.ClusteringTask() & session_key

# We are then able to populate the clustering results. The `Clustering` table now validates the Kilosort2 outcomes before ingesting the spike sorted results. In the future release of elements-ephys, this table will be used to trigger Kilosort2. A record in the `Clustering` indicates that Kilosort2 job is done successfully and the results are ready to be processed.

ephys.Clustering.populate(display_progress=True)

ephys.Clustering() & session_key

# ## Import clustering results and manually curated results

# We are now ready to ingest the clustering results (spike times etc.) into the database. These clustering results are either directly from Kilosort2 or with manual curation. Both ways share the same format of files. In the element, there is a `Curation` table that saves this information.

dj.Diagram(ephys.ClusteringTask) + dj.Diagram(ephys.Clustering) + dj.Diagram(ephys.Curation) + \
dj.Diagram(ephys.CuratedClustering) + dj.Diagram(ephys.CuratedClustering.Unit)

key = (ephys.ClusteringTask & session_key).fetch1('KEY')
ephys.Curation().create1_from_clustering_task(key)
ephys.Curation() & session_key

# Then we could populate table `CuratedClustering`, ingesting either the output of Kilosort2 or the curated results.

ephys.CuratedClustering.populate(session_key, display_progress=True)

# The part table `CuratedClustering.Unit` contains the spike sorted units

ephys.CuratedClustering.Unit()

# ## Populate LFP

# + `LFP`: mean of LFP across all electrodes for a from a given Ephys recording
# + `LFP.Electrode`: LFP of selected electrodes

# + LFP and LFP.Electrode: By populating LFP, LFP of every other 9 electrode on the probe will be saved into table `ephys_element.LFP.Electrode` and an average LFP saved into table `ephys_element.LFP`
dj.Diagram(ephys.EphysRecording) + dj.Diagram(ephys.LFP) + dj.Diagram(ephys.LFP.Electrode)
# -

# Takes a few minutes to populate
ephys.LFP.populate(session_key, display_progress=True)
ephys.LFP & session_key

# ## Populate Spike Waveform

# The current workflow also contain tables to save spike Waveforms:
# + `WaveformSet`: a table to drive the processing of all spikes waveforms resulting from a given Clustering or CuratedClustering.
# + `WaveformSet.Waveform`: mean waveform across spikes for a given unit and electrode.
# + `WaveformSet.PeakWaveform`: mean waveform across spikes for a given unit at the electrode with peak spike amplitude.

dj.Diagram(ephys.CuratedClustering) + dj.Diagram(ephys.WaveformSet) + 1

# + The `probe_element.EelectrodeConfig` table conains the configuration information of the electrodes used, i.e. which 384 electrodes out of the total 960 on the probe were used in this ephys session, while the table `ephys_element.EphysRecording` specify which ElectrodeConfig is used in a particular ephys session.
ephys_.Waveform.populate(session_key, display_progress=True)
# -

ephys_element.LFP.Electrode & session_key
