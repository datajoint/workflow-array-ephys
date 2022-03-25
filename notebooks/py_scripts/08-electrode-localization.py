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
#     display_name: venv-nwb
#     language: python
#     name: venv-nwb
# ---

# # Electrode Localization

# Change into the parent directory to find the `dj_local_conf.json` file.

import os
import datajoint as dj
# change to the upper level folder to detect dj_local_conf.json
if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')
assert os.path.basename(os.getcwd())=='workflow-array-ephys', ("Please move to the "
                                                               + "workflow directory")

# + [markdown] jp-MarkdownHeadingCollapsed=true tags=[]
# ## Coordinate Framework
# -

# The Allen Institute hosts [brain atlases](http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017) and [ontology trees](https://community.brain-map.org/t/allen-mouse-ccf-accessing-and-using-related-data-and-tools/359) that we'll use in the next section. The `localization.py` script assumes this is your first atlas, and that you'll use the 100μm resolution. For finer resolutions, edit `voxel_resolution` in `localization.py`. Higher resolution `nrrd` files are quite large when loaded. Depending on the python environment, the terminal may be killed when loading so much information into memory. To load multiple atlases, increment `ccf_id` for each unique atlas.
#
# To run this pipeline ...
# 1. Download the 100μm `nrrd` and `csv` files from the links above.
# 2. Move these files to your ephys root directory.

# Next, we'll populate the coordinate framework schema simply by loading it.

from workflow_array_ephys.localization import coordinate_framework as ccf

# Now, to explore the data we just loaded.

ccf.BrainRegionAnnotation.BrainRegion()

# Let's look at the dimensions of the primary somatosensory cortex, which has the acronym `SSp1`. To look at other regions, open the CSV you downloaded and search for your desired region.

ccf.BrainRegionAnnotation.Voxel() & 'acronym="SSp1"'

# ## Electrode Localization

# If you have `channel_location` json files for your data, you can look at the position and regions associated with each electrode. Here, we've added an example file to our pre-existing `subject6` for demonstration purposes.

dj.config.load('dj_local_conf.json')
from workflow_array_ephys.pipeline import subject, session, ephys, probe
from workflow_array_ephys.localization import electrode_localization as eloc

from workflow_array_ephys.localization import coordinate_framework as ccf

eloc.ElectrodePosition.populate()
eloc.ElectrodePosition.Electrode()


