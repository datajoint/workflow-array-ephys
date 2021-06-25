# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: workflow-array-ephys
#     language: python
#     name: workflow-array-ephys
# ---

# # Electrophysiology 101

# Neuronal electrophysiology (ephys) refers to the study of the electrical properties of cells and tissue in the nervous system. Ephys is one of the <em>most prevalent</em> types of studies in the field of Neuroscience and its benefits cannot be overstated. One type of ephys experiment is called extracellular electrophysiology which involves inserting a probe into the tissue of interest and studying the surrounding electrical activity in the presence of a stimulus.
#     
# While there are many ways to conduct an ephys experiment and structure its processing and analysis, the scope of the workflow described below refers to the approach DataJoint has taken as a result of extensive collaboration with neuroscience laboratories around the world.
#     
# ### General Structure
#    
# 1. The electrode arrays (probes) are inserted into the brain-area of interest. 
# 2. The user decides which area of the probe will be used (i.e a subset of the total number of electrodes.).
# 3. The researcher conducts the experiment, usually presenting some stimuli to the subject. 
# 4. The raw data is collected and clustered.
# 5. The data is further divided into the units, spike times, and waveforms.
#
#     
# More on Clustering:
# The clustering analysis processes raw data and retrieves units, spiketimes, and waveforms.
#
#
#
#
#
#
#
#
#

# ![Array%20Electropshyiology-Cartoonify%203.png](attachment:Array%20Electropshyiology-Cartoonify%203.png)

subject_table = dj.Diagram(probe) + ephys.ProbeInsertion + ephys.InsertionLocation + subject.Subject
subject_table.save('SUBJET.svg', format='svg')

subject.Subject()

probe.ProbeType.Electrode & 'probe_type LIKE "%2.0%"'

ephys.EphysRecording & ephys.ClusteringTask

dj.Diagram(ephys)

import datajoint as dj
help(dj.Diagram)

dj.Diagram(ephys).save('EPHYS.svg', format='svg')

# ![EPHYS.svg](attachment:EPHYS.svg)

clustering = dj.Diagram(ephys.Curation) + ephys.CuratedClustering.Unit +ephys.CuratedClustering+ ephys.Clustering + ephys.ClusteringMethod + ephys.ClusteringParamSet + ephys.ClusteringTask + ephys.ClusterQualityLabel
clustering.save('clustering.svg', format = 'svg')

new_probe = dj.Diagram(probe)
new_probe.save('newprobe.svg',format='svg')

ephys_and_friends = dj.Diagram(ephys.EphysRecording) + ephys.ClusteringTask + ephys.Clustering + ephys.EphysRecording.EphysFile + ephys.ClusteringParamSet + ephys.ClusteringMethod

probe.ProbeType & probe.ElectrodeConfig

ephys_and_friends.save('newEphys.svg', format = 'svg')

dj.Diagram(ephys.EphysRecording) + ephys.ClusteringTask + ephys.Clustering + ephys.EphysRecording.EphysFile + ephys.ClusteringParamSet + ephys.ClusteringMethod

# # Introduction to the workflow structure

# This notebook gives a brief overview of the workflow structure and introduces some useful DataJoint tools to facilitate the exploration.
# + DataJoint needs to be pre-configured before running this notebook, if you haven't set up the configuration, refer to notebook [01-configure](01-configure.ipynb).
# + If you are familar with DataJoint and the workflow structure, proceed to the next notebook [03-process](03-process.ipynb) directly to run the workflow.
# + For a more thorough introduction of DataJoint functionings, please visit our [general tutorial site](https://playground.datajoint.io)

# To load the local configuration, we will change the directory to the package root.

import os
os.chdir('..')

# ## Schemas and tables

# The current workflow is composed of multiple database schemas, each of them corresponds to a module within `workflow_array_ephys.pipeline`

import datajoint as dj
from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

# ls

# + Each module contains a schema object that enables interaction with the schema in the database.
probe.schema

# + Each module imported above corresponds to one schema inside the database. For example, `ephys` corresponds to `neuro_ephys` schema in the database.
ephys.schema

# + The table classes in the module correspond to a table in the schema in the database.



# + Each datajoint table class inside the module corresponds to a table inside the schema. For example, the class `ephys.EphysRecording` correponds to the table `_ephys_recording` in the schema `neuro_ephys` in the database.
# preview table columns and contents in a table
ephys.EphysRecording()

# + By importing the modules for the first time, the schemas and tables will be created inside the database.
ephys.EphysRecording()


# + Once created, importing modules will not create schemas and tables again, but the existing schemas/tables can be accessed and manipulated by the modules.

# -
# ## DataJoint tools to explore schemas and tables

# + `dj.list_schemas()`: list all schemas a user has access to in the current database
dj.Diagram()

# + `dj.list_schemas()`: list all schemas a user could access.
dj.list_schemas()

# + `dj.Diagram()`: plot tables and dependencies
# plot diagram for all tables in a schema
dj.Diagram(ephys)
# -

# ## The ephys diagram shows us the real world elements that the tables are modeling. 

# ![Array%20Electropshyiology-first%20subset.png](attachment:Array%20Electropshyiology-first%20subset.png)

# **Table tiers**: 
#
# Manual table: green box, manually inserted table, expect new entries daily, e.g. Subject, ProbeInsertion.  
# Lookup table: gray box, pre inserted table, commonly used for general facts or parameters. e.g. Strain, ClusteringMethod, ClusteringParamSet.  
# Imported table: blue oval, auto-processing table, the processing depends on the importing of external files. e.g. process of Clustering requires output files from kilosort2.  
# Computed table: red circle, auto-processing table, the processing does not depend on files external to the database, commonly used for     
# Part table: plain text, as an appendix to the master table, all the part entries of a given master entry represent a intact set of the master entry. e.g. Unit of a CuratedClustering.
#
# **Dependencies**:  
#
# One-to-one primary: thick solid line, share the exact same primary key, meaning the child table inherits all the primary key fields from the parent table as its own primary key.     
# One-to-many primary: thin solid line, inherit the primary key from the parent table, but have additional field(s) as part of the primary key as well
# secondary dependency: dashed line, the child table inherits the primary key fields from parent table as its own secondary attribute.

# + `dj.Diagram()`: plot the diagram of the tables and dependencies. It could be used to plot tables in a schema or selected tables.
# plot diagram of tables in multiple schemas
dj.Diagram(subject) + dj.Diagram(session) + dj.Diagram(ephys)

# +
#Show how the subject, session, and diagram are connected via diagram
# -

# plot diagram of selected tables and schemas
dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + dj.Diagram(ephys)

ephys.CuratedClustering()

# plot diagram with 1 additional level of dependency downstream
dj.Diagram(subject.Subject) + 1

# plot diagram with 2 additional levels of dependency upstream
dj.Diagram(ephys.EphysRecording) - 2

# ![Array%20Electropshyiology-probe%20info%20%282%29.svg](attachment:Array%20Electropshyiology-probe%20info%20%282%29.svg)

probe_and_session = dj.Diagram(probe) + subject.Subject + session.Session + ephys.ProbeInsertion + ephys.InsertionLocation
probe_and_session.save('probeandsession.svg', format='svg')

# <hr>

# ## Checkpoint 2
# If I was at the examining the data at the ephys.ClusteringTask table, and I wanted more data regarding the subject regarding the subject's zygosity, what schema and table could I use to find that information? (Hint: You can trace the pipeline, explore different schemas to find this answer). 

# <hr>

# + `describe()`: show table definition with foreign key references.

ephys.EphysRecording.describe();

# <hr/>
# -

probe.ProbeType()

# +
#The bottom three cells are just a space for me to explore a little 
# -

#First table
ephys.ProbeInsertion()

ephys.AcquisitionSoftware()

ephys.EphysRecording()

# <hr/>

# + `heading`: show attribute definitions regardless of foreign key references



# + `heading`: show table attributes regardless of foreign key references.
ephys.EphysRecording.heading
# -

# <hr>

# ## Checkpoint 3
# What is the difference between the `.heading` attribute and the `.describe()` method? 

# <hr>

# + probe [markdown]
# # Major DataJoint Elements installed in the current workflow
# + [`lab`](https://github.com/datajoint/element-lab): lab management related information, such as Lab, User, Project, Protocol, Source.

# -

dj.Diagram(lab)

ephys.EphysRecording()

help(ephys.EphysRecording())

# + [`subject`](https://github.com/datajoint/element-animal): general animal information, User, Genetic background, Death etc.

dj.Diagram(subject)

# + [subject](https://github.com/datajoint/element-animal): contains the basic information of subject, including Strain, Line, Subject, Zygosity, and SubjectDeath information.
subject.Subject.describe();
# -

# ![Array%20Electropshyiology-Subject%20%281%29.svg](attachment:Array%20Electropshyiology-Subject%20%281%29.svg)

# + [`session`](https://github.com/datajoint/element-session): General information of experimental sessions.

dj.Diagram(session)

# + [session](https://github.com/datajoint/element-session): experimental session information
session.Session.describe();

# + [`ephys`](https://github.com/datajoint/element-array-ephys): Neuropixel based probe and ephys information



# + [probe and ephys](https://github.com/datajoint/element-array-ephys): Neuropixel based probe and ephys tables
dj.Diagram(probe) + dj.Diagram(ephys)
# -

ephys.LFP()

ephys.LFP.Electrode()

# ![Array%20Electropshyiology-ephys%20recording.png](attachment:Array%20Electropshyiology-ephys%20recording.png)

# ## Summary and next step
#
# + This notebook introduced the overall structures of the schemas and tables in the workflow and relevant tools to explore the schema structure and table definitions.
#
# + In the next notebook [03-process](03-process.ipynb), we will further introduce the detailed steps running through the pipeline and table contents accordingly.

# ## Question Categories
# ### DataJoint Questions
# Question type:
# 1. Theory
# 2. Recall (from information contained in notebook02)
# 3. Inference/Recall
# 4. Inference
# 5. Recall
#
#
# ### Workflow Questions
# Question type:
# 1. Exploratory
# 2. Exploratory
# 3. Inference
# 4. Understanding 
# 5. 
#

# ## DataJoint Questions
# 1. What is the difference between the `.heading` attribute and the `.describe()` method?
# 2. The `ephys.EphysRecording` table is shown in the Diagram inside a blue bubble, while `ephys.ProbeInsertion` is shown in a green box. What do the color differences tell us about these tables? 
# 3. We see in the `ephys.LFP.Electrode` table that the primary keys are inherited from the `ephys.LFP` table and the `probe.ElectrodeConfig.Electrode` table. What does this tell us about the way inheritance can work across schemas? 
# 4. What does `ephys.EphysRecording` being connected to `ephys.LFP` by a thick, solid tell me? 
# 5. What do the dashed lines tell me about the relationship between ephys.AcquisitionSoftware and ephys.EphysRecording?

# ## Workflow Questions
# 1. Which table tells us the probe and electrode a unit is coming from? (Hint: You can hover over the tables diagram to see their fields.)
# 2. If I was at the examining the data at the `ephys.EphysRecording` table, and I wanted more data regarding the subject regarding the subject's zygosity, what schema and table could I use to find that information? (Hint: You can trace the pipeline, explore different schemas to find this answer).
# 3. The tables `ephys.ClusteringTask` and `ephys.Curation` both have a field pointing Datajoint to an output directory. Under what conditions would these fields be the same? Under what conditions would these fields be different?
# 4. What is the difference between `ephys.WaveformSet.PeakWaveform` and `ephys.WaveformSet.Waveform`?(Hint: look at the fields in both.)
# 5. 




