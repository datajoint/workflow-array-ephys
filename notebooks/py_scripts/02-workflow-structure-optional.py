# -*- coding: utf-8 -*-
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
#     display_name: Python 3.9.12 ('ele')
#     language: python
#     name: python3
# ---

# # Introduction to the workflow structure

# This notebook gives an overview of the workflow structure and introduces useful DataJoint tools for exploration.
# + DataJoint needs to be configured before running this notebook. If you haven't done so, refer to notebook [01-configure](01-configure.ipynb).
# + If you are familar with DataJoint workflow structures, proceed to the next notebook [03-process](03-process.ipynb) directly to run this workflow.
# + For a more thorough introduction of DataJoint functions, please visit our [general documentation](https://docs.datajoint.org/python/v0.13/index.html)

# To load the local configuration, we will change the directory to the package root.

import os
if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")

# ## Schemas, Diagrams and Tables

# Schemas are conceptually related sets of tables. By importing schemas from `workflow_array_ephys.pipeline`, we'll declare the tables on the server with the prefix in the config (if we have permission to do so). If these tables are already declared, we'll gain access. 
#
# - `dj.list_schemas()` lists all schemas a user has access to in the current database
# - `<schema>.schema.list_tables()` will provide names for each table in the format used under the hood.

import datajoint as dj
from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

probe.schema

# + Each module imported above corresponds to one schema inside the database. For example, `ephys` corresponds to `neuro_ephys` schema in the database.
ephys.schema.list_tables()
# -

# `dj.Diagram()` plots tables and dependencies in a schema. To see additional upstream or downstream connections, add `- N` or `+ N`.
#
# - `probe`: Neuropixels-based probe information
# - `ephys`: Electrophysiology data

# + `dj.Diagram()`: plot tables and dependencies
# plot diagram for all tables in a schema
dj.Diagram(probe)
# -

dj.Diagram(ephys) + dj.Diagram(session) - 1

# ### Table Types
#
# - **Manual table**: green box, manually inserted table, expect new entries daily, e.g. Subject, ProbeInsertion.  
# - **Lookup table**: gray box, pre inserted table, commonly used for general facts or parameters. e.g. Strain, ClusteringMethod, ClusteringParamSet.  
# - **Imported table**: blue oval, auto-processing table, the processing depends on the importing of external files. e.g. process of Clustering requires output files from kilosort2.  
# - **Computed table**: red circle, auto-processing table, the processing does not depend on files external to the database, commonly used for     
# - **Part table**: plain text, as an appendix to the master table, all the part entries of a given master entry represent a intact set of the master entry. e.g. Unit of a CuratedClustering.
#
# ### Table Links
#
# - **One-to-one primary**: thick solid line, share the exact same primary key, meaning the child table inherits all the primary key fields from the parent table as its own primary key.     
# - **One-to-many primary**: thin solid line, inherit the primary key from the parent table, but have additional field(s) as part of the primary key as well
# - **Secondary dependency**: dashed line, the child table inherits the primary key fields from parent table as its own secondary attribute.

# ## Common Table Functions

#
# - `<table>()` show table contents
# - `heading` shows attribute definitions
# - `describe()` show table definition with foreign key references

# + Each datajoint table class inside the module corresponds to a table inside the schema. For example, the class `ephys.EphysRecording` correponds to the table `_ephys_recording` in the schema `neuro_ephys` in the database.
# preview table columns and contents in a table
ephys.EphysRecording()
# -

ephys.Clustering.heading

ephys.WaveformSet.describe()

# + probe [markdown]
# ## Other Elements installed with the workflow
#
# - [`lab`](https://github.com/datajoint/element-lab): lab management related information, such as Lab, User, Project, Protocol, Source.
# - [`subject`](https://github.com/datajoint/element-animal): (element-animal) general animal information, User, Genetic background, Death etc.
# - [`session`](https://github.com/datajoint/element-session): General information of experimental sessions.
#
# For more information about these Elements, see [workflow session](https://github.com/datajoint/workflow-session).
# -
dj.Diagram(lab)

dj.Diagram(subject)

# + [subject](https://github.com/datajoint/element-animal): contains the basic information of subject, including Strain, Line, Subject, Zygosity, and SubjectDeath information.
subject.Subject.describe()
# -

dj.Diagram(session)

# ## Summary and next step
#
# + This notebook introduced the overall structures of the schemas and tables in the workflow and relevant tools to explore the schema structure and table definitions.
#
# + In the next notebook [03-process](03-process.ipynb), we will further introduce the detailed steps running through the pipeline and table contents accordingly.
