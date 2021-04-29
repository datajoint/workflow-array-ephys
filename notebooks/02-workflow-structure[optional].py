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

# # Introduction to the workflow structure

# This notebook gives a brief overview of the workflow structure and introduce some useful DataJoint tools to facilitate the exploration.
# + DataJoint needs to be pre-configured before running this notebook, if you haven't set up the configuration, refer to notebook [01-configuration](01-configuration.ipynb).
# + If you are familar with DataJoint and the workflow structure, proceed to the next notebook [03-process](03-process.ipynb) directly to run the workflow.
# + For a more thorough introduction of DataJoint functionings, please visit our [general tutorial site](https://playground.datajoint.io)

# To load the local configuration, we will change the directory to the package root.

import os
os.chdir('..')

# ## Schemas and tables

# The current workflow is composed of multiple database schemas, each of them corresponds to a module within `workflow_array_ephys.pipeline`

import datajoint as dj
from workflow_array_ephys.pipeline import lab, subject, session, probe, ephys

# + Inside each module, there is was a schema object links the module with the schema inside the database. e.g. ephys corresponds to `neuro_ephys` in the database.

# + Each module imported above corresponds to one schema inside the database. For example, `ephys` corresponds to `neuro_ephys` schema in the database.
ephys.schema

# + The table classes inside the module correspond to a table inside the database. e.g. the class ephys.EphysRecording corresponds to table `_ephys_recording` in schema `neuro_ephys`

# show the table name on the database side.
ephys.EphysRecording.table_name

# + Each datajoint table class inside the module corresponds to a table inside the schema. For example, the class `ephys.EphysRecording` correponds to the table `_ephys_recording` in the schema `neuro_ephys` in the database.
# preview table columns and contents in a table
ephys.EphysRecording()

# + The first time importing the modules, empty schemas and tables will be created in the database. [markdown]
# # + By importing the modules for the first time, the schemas and tables will be created inside the database.
# # + Once created, importing modules will not create schemas and tables again, but the existing schemas/tables can be accessed and manipulated by the modules.
# -
# ## DataJoint tools to explore schemas and tables

# + The schemas and tables will not be re-created when importing modules if they have existed. [markdown]
# # + `dj.list_schemas()`: list all schemas a user has access to
# + `dj.list_schemas()`: list all schemas a user could access.
dj.list_schemas()

# + `list_tables()`: list the tables in the database within a schema.

# + `list_tables()`: list tables inside a schema
ephys.schema.list_tables()

# + `dj.Diagram()`: plot tables and dependencies

# plot diagram for all tables in a schema
dj.Diagram(ephys)

# **Table tiers**: 
#
# Manual table: green box, manually inserted table, expect new entries daily, e.g. Subject, ProbeInsertion.  
# Lookup table: gray box, pre inserted table, commonly used for general facts or parameters. e.g. Strain, ClusteringMethod, ClusteringParamSet.  
# Imported table: blue oval, auto-processing table, the processing depends on the importing of external files. e.g. process of Clustering requires output files from kilosort2.  
# Computed table: red circle, auto-processing table, the processing does not depend on files external to the database, commonly used for     
# Part table: plain text
#
# **Dependencies**:  
#
# One-to-one primary: thick solid line, share the exact same primary key, meaning the child table inherits all the primary key fields from the parent table as its own primary key.     
# One-to-many primary: thin solid line, inherit the primary key from the parent table, but have additional field(s) as part of the primary key as well
# secondary dependency: dashed line, the child table inherits the primary key fields from parent table as its own secondary attribute.

# + `dj.Diagram()`: plot the diagram of the tables and dependencies. It could be used to plot tables in a schema or selected tables.
# plot diagram of tables in multiple schemas
dj.Diagram(subject) + dj.Diagram(session) + dj.Diagram(ephys)
# -

# plot diagram of selected tables and schemas
dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + dj.Diagram(ephys)

# + `heading`: [markdown]
# # + `describe()`: show table definition with foreign key references.
# -
ephys.EphysRecording.describe();

# + `heading`: show table attributes regardless of foreign key references.

ephys.EphysRecording.heading

# + probe [markdown]
# # Major DataJoint Elements installed in the current workflow
# + ephys [markdown]
# # + [lab](https://github.com/datajoint/element-lab): lab management related information, such as Lab, User, Project, Protocol, Source.
# -

dj.Diagram(lab)

# + [subject](https://github.com/datajoint/element-animal): contains the basic information of subject, including Strain, Line, Subject, Zygosity, and SubjectDeath information.

dj.Diagram(subject)

subject.Subject.describe();

# + [session](https://github.com/datajoint/element-session): experimental session information

dj.Diagram(session)

session.Session.describe();

# + [probe and ephys](https://github.com/datajoint/element-array-ephys): Neuropixel based probe and ephys tables

dj.Diagram(probe) + dj.Diagram(ephys)

# ## Summary and next step

# This notebook introduced the overall structures of the schemas and tables in the workflow and relevant tools to explore the schema structure and table definitions.
#
# In the next notebook [03-process](03-process.ipynb), we will further introduce the detailed steps running through the pipeline and table contents accordingly.


