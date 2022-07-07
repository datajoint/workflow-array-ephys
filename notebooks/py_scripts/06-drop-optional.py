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
#     display_name: Python [conda env:workflow-ephys]
#     language: python
#     name: conda-env-workflow-ephys-py
# ---

# # Drop schemas
#
# + Schemas are not typically dropped in a production workflow with real data in it.
# + At the developmental phase, it might be required for the table redesign.
# + When dropping all schemas is needed, the following is the dependency order.

# Change into the parent directory to find the `dj_local_conf.json` file.

import os

os.chdir("..")

# +
from workflow_array_ephys.pipeline import *

# ephys.schema.drop()
# probe.schema.drop()
# session.schema.drop()
# subject.schema.drop()
# lab.schema.drop()
