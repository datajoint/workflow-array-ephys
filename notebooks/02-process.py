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
#     display_name: bl_dev
#     language: python
#     name: bl_dev
# ---

# # Run array ephys workflow

# This notebook walks you through the steps to run the ephys workflow.  
# The workflow requires neuropixels meta file and kilosort output data. To configure the paths properly, refer to [00-Set_up_the_configuration_file](./00-Set_up_the_configuration_file.ipynb)

# To load the local configuration, we will change the directory to the package root.

import os
os.chdir('../..')

#
# Let's start by importing the relevant modules.

import datajoint as dj
from bl_pipeline import lab, subject, acquisition
from bl_pipeline.ephys_element import ephys_element, probe_element

# # Pipeline structure

# + `dj.Diagram` enables checking pipeline structure and table dependencies. [markdown]
# # + dj.Diagram is a useful command to visualize the workflow structure and table dependencies.
# # + Major DataJoint Elements installed in the current workflow:
#     + lab
#     + subject
#     + session
#     + probe
#     + ephys
# +
## conn.list_schemas, schema.list_tables, Diagram and describe

# + Two DataJoint elements `probe_element` and `ephys_element` have been installed into `bl_pipeline`
dj.Diagram(subject.Rats) + dj.Diagram(acquisition.Sessions) + dj.Diagram(probe_element) + dj.Diagram(ephys_element)
# -

# ## Ingestion of subjects, sessions, probes data
# Extract user-specified information from `/user_data/subjects.csv` and `/user_data/sessions.csv` and insert into corresponding tables:
# + subject.Subject
# + Session
# + probe.Probe
# + ephys.ProbeInsertion

Manually ingest subjects, sessions (Probe.insert1(...))
ingest.ingest_subjects()

Introduce the automatic functions

# + For chornic probe insertions, `ephys_element.ProbeInsertion` directly depends on `subject.Rats` [markdown]
# ## Ephys element starts with table `ProbeInsertion`, as a child table of `subject.Rats`
# + Each entry in the table `acquisition.Sessions` describes an experimental session within a particular date.
dj.Diagram(subject.Rats) + dj.Diagram(acquisition.Sessions) + dj.Diagram(probe_element.Probe) + \
(dj.Diagram(ephys_element.ProbeInsertion) + 1)
# + In this experiment with chronic probe insertions, the table `ephys_element.ProbeInsertion` directly depends on `subject.Rats`
# + Each entry in `acquisition.Sessions` represents an experimental session on a particular date.
# + Each entry in `ephys_element.EphysRecording` is for a particular probe insertion and a session.

# As an example, we will work on the following session throughout the notebook:

# + For each combination of `acquisition.Sessions` and `ephys_element.ProbeInsertion`, there is a `ephys_element.EphysRecording`
session_key = (acquisition.Sessions & 'session_rat="A256"' & 'session_date="2020-09-28"').fetch1('KEY')
acquisition.Sessions & session_key
# -
# ## Ingest Probe and ProbeInsertion by ephys_element_ingest

dj.Diagram(probe_element.Probe) + acquisition.Sessions + ephys_element.EphysRecording

# A module `ephys_element_ingest` was provided to process a ephys session based on the neuropixel meta file: ingest entries into tables `Probe` and `ProbeInsertion`

from bl_pipeline.ingest import ephys_element_ingest
ephys_element_ingest.process_session(session_key)

# As a result, there will contents in the following tables:

probe_element.Probe()

ephys_element.ProbeInsertion()

# ## Populate EphysRecording

dj.Diagram(acquisition.Sessions) + (dj.Diagram(probe_element.ElectrodeConfig) + 1) + \
ephys_element.EphysRecording + ephys_element.EphysRecording.EphysFile

# first argument restricts the populate to a particular subset.
ephys_element.EphysRecording.populate(session_key, display_progress=True)

# Populate EphysRecording extracts the following information from .ap.meta file from SpikeGLX:
#
# 1. **probe_element.EelectrodeConfig**: this procedure detects new ElectrodeConfig, i.e. which 384 electrodes out of the total 960 on the probe were used in this ephys session, and save the results into the table `probe_element.EelectrodeConfig`. Each entry in table `ephys_element.EphysRecording` specifies which ElectrodeConfig is used in a particular ephys session. 

# For this ephys session we just populated, Electrodes 0-383 was used.

probe_element.ElectrodeConfig()

probe_element.ElectrodeConfig.Electrode()

# 2. **ephys_element.EphysRecording**: note here that it refers to a particular electrode_config identified with a hash.

ephys_element.EphysRecording() & session_key

# 3. **ephys_element.EphysRecording.EphysFile**

ephys_element.EphysRecording.EphysFile() & session_key

# ## Create ClusteringTask and run/validate Clustering

dj.Diagram(ephys_element.EphysRecording) + ephys_element.ClusteringParamSet + ephys_element.ClusteringTask + \
ephys_element.Clustering

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
ephys_element.ClusteringParamSet.insert_new_params(
    'kilosort2', 0, 'Spike sorting using Kilosort2', params_ks)
ephys_element.ClusteringParamSet()

# We are then able to insert an entry into the `ClusteringTask` table. One important field of the table is `clustering_output_dir`, which specifies the Kilosort2 output directory for the later processing.  
# **Note**: this output dir is a relative path to be combined with `clustering_root_directory` in the config file.

ephys_element.ClusteringTask.insert1(
    dict(session_key, ratname='A256', insertion_number=0, paramset_idx=0,
         clustering_output_dir='NP_sorted/Adrian/A256/A256_2020_09_28/A256_2020_09_28_g0/spikesort_2020_11_23_09_09_42_ks2jrc'),
    skip_duplicates=True)

ephys_element.ClusteringTask() & session_key

# We are then able to populate the clustering results. The `Clustering` table now validates the Kilosort2 outcomes before ingesting the spike sorted results. In the future release of elements-ephys, this table will be used to trigger Kilosort2. A record in the `Clustering` indicates that Kilosort2 job is done successfully and the results are ready to be processed.

ephys_element.Clustering.populate(display_progress=True)

ephys_element.Clustering() & session_key

# ## Import clustering results and manually curated results

# We are now ready to ingest the clustering results (spike times etc.) into the database. These clustering results are either directly from Kilosort2 or with manual curation. Both ways share the same format of files. In the element, there is a `Curation` table that saves this information.

dj.Diagram(ephys_element.ClusteringTask) + ephys_element.Clustering + ephys_element.Curation + \
ephys_element.CuratedClustering + ephys_element.CuratedClustering.Unit

# + If a manual curation was implemented, an entry needs to be manually inserted into the table `Curation`, which specifies the directory to the curated results in `curation_output_dir`.
#
# + If we would like to process the Kilosort2 outcome directly, an entry is also needed in `Curation`. A method `create1_from_clustering_task` was provided to help this insertion. It copies the `clustering_output_dir` in `ClusteringTask` to the field `curation_output_dir` in the table `Curation` with a new `curation_id`.

key = (ephys_element.ClusteringTask & session_key).fetch1('KEY')
ephys_element.Curation().create1_from_clustering_task(key)
ephys_element.Curation() & session_key

# Then we could populate table `CuratedClustering`, ingesting either the output of Kilosort2 or the curated results.

ephys_element.CuratedClustering.populate(session_key, display_progress=True)

# The part table `CuratedClustering.Unit` contains the spike sorted units

ephys_element.CuratedClustering.Unit()

# ## Populate LFP and spike waveform

# There are two additional tables in the ephys_element that is able to get automatically processed:
# + LFP and LFP.Electrode: By populating LFP, LFP of every other 9 electrode on the probe will be saved into table `ephys_element.LFP.Electrode` and an average LFP saved into table `ephys_element.LFP`

dj.Diagram(ephys_element.EphysRecording) + ephys_element.LFP + ephys_element.LFP.Electrode

ephys_element.LFP.populate(session_key, display_progress=True)
ephys_element.LFP & session_key

ephys_element.LFP.Electrode & session_key

dj.Diagram(ephys_element.CuratedClustering.Unit) + ephys_element.Waveform

# + Waveform: `Waveform` table computes the average spike waveform of the channel with peak amplitudes. It takes a while to populate depending on the size of the data.

# + The `probe_element.EelectrodeConfig` table conains the configuration information of the electrodes used, i.e. which 384 electrodes out of the total 960 on the probe were used in this ephys session, while the table `ephys_element.EphysRecording` specify which ElectrodeConfig is used in a particular ephys session.
ephys_element.Waveform.populate(session_key, display_progress=True)
# -

ephys_element.LFP.Electrode & session_key
