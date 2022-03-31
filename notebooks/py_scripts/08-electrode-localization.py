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
# change to the upper level folder to detect dj_local_conf.json
if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')
assert os.path.basename(os.getcwd())=='workflow-array-ephys', ("Please move to the "
                                                               + "workflow directory")
# We'll be working with long tables, so we'll make visualization easier with a limit
import datajoint as dj; dj.config['display.limit']=10

# + [markdown] tags=[] jp-MarkdownHeadingCollapsed=true jp-MarkdownHeadingCollapsed=true tags=[]
# ## Coordinate Framework
# -

# The Allen Institute hosts [brain atlases](http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017) and [ontology trees](https://community.brain-map.org/t/allen-mouse-ccf-accessing-and-using-related-data-and-tools/359) that we'll use in the next section. The `localization.py` script assumes this is your first atlas, and that you'll use the 100μm resolution. For finer resolutions, edit `voxel_resolution` in `localization.py`. Higher resolution `nrrd` files are quite large when loaded. Depending on the python environment, the terminal may be killed when loading so much information into memory. To load multiple atlases, increment `ccf_id` for each unique atlas.
#
# To run this pipeline ...
# 1. Download the 100μm `nrrd` and `csv` files from the links above.
# 2. Move these files to your ephys root directory.

# Next, we'll populate the coordinate framework schema simply by loading it. Because we are loading the whole brain volume, this may take 25 minutes or more.

from workflow_array_ephys.localization import coordinate_framework as ccf

# Now, to explore the data we just loaded.

ccf.BrainRegionAnnotation.BrainRegion()

# The acronyms listed in the DataJoint table differ slightly from the CCF standard by substituting case-sensitive differences with [snake case](https://en.wikipedia.org/wiki/Snake_case). To lookup the snake case equivalent, use the `retrieve_acronym` function.

central_thalamus = ccf.BrainRegionAnnotation.retrieve_acronym('CM')
cranial_nerves = ccf.BrainRegionAnnotation.retrieve_acronym('cm')
print(f'CM: {central_thalamus}\ncm: {cranial_nerves}')

# If your work requires the case-sensitive columns please contact get in touch with the DataJoint team via [StackOverflow](https://stackoverflow.com/questions/tagged/datajoint).
#
# For this demo, let's look at the dimensions of the central thalamus. To look at other regions, open the CSV you downloaded and search for your desired region.

cm_voxels = ccf.BrainRegionAnnotation.Voxel() & f'acronym=\"{central_thalamus}\"'
cm_voxels

cm_x, cm_y, cm_z = cm_voxels.fetch('x', 'y', 'z')
print(f'The central thalamus extends from \n\tx = {min(cm_x)}  to x = {max(cm_x)}\n\t'
      + f'y = {min(cm_y)} to y = {max(cm_y)}\n\tz = {min(cm_z)} to z = {max(cm_z)}')

# ## Electrode Localization

# If you have `channel_location` json files for your data, you can look at the position and regions associated with each electrode. Here, we've added an example file to our pre-existing `subject6` for demonstration purposes.

from workflow_array_ephys.localization import coordinate_framework as ccf
from workflow_array_ephys.localization import electrode_localization as eloc

# Because the probe may not be fully inserted, there will be some electrode positions that occur outside the brain. We register these instances with an `IntegrityError` warning because we're trying to register a coorinate position with no corresponding location in the `ccf.CCF.Voxel` table. We can silence these warnings by setting the log level before running `populate()` on the `ElectrodePosition` table.

import logging
logging.getLogger().setLevel(logging.ERROR) # or logging.INFO

eloc.ElectrodePosition.populate()

# By calling the `ElectrodePosition` table, we can see the keys the `populate()` method has already processed.

eloc.ElectrodePosition()

# Let's focus on `subject5`, insertion `1`.

from workflow_array_ephys.pipeline import ephys
key=(ephys.EphysRecording & 'subject="subject5"' & 'insertion_number=1').fetch1('KEY')
len(eloc.ElectrodePosition.Electrode & key)

# With a resolution of 100μm, adjacent electrodes will very likely be in the same region. Let's look at every 38th electrode to sample 10 across the probe.
#
# If you're interested in more electrodes, decrease the number next to the `%` modulo operator.

electrode_coordinates = (eloc.ElectrodePosition.Electrode & 'electrode%38=0' 
                         & key).fetch('electrode', 'x', 'y', 'z', as_dict=True)
for e in electrode_coordinates:
    x, y, z = [ e[k] for k in ('x','y', 'z')]
    acronym = (ccf.BrainRegionAnnotation.Voxel & f'x={x}' & f'y={y}' & f'z={z}'
               ).fetch1('acronym')
    e['region'] = (ccf.BrainRegionAnnotation.BrainRegion & f'acronym=\"{acronym}\"'
                   ).fetch1('region_name')
    print('Electrode {electrode} (x={x}, y={y}, z={z}) is in {region}'.format(**e))


