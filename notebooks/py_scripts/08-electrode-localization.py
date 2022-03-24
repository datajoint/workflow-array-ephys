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

# The Allen Institute hosts [brain atlases](http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017) and [ontology trees](https://community.brain-map.org/t/allen-mouse-ccf-accessing-and-using-related-data-and-tools/359) that we'll use in the next section.
# 1. Download the `nrrd` and `csv` files that correspond too your desired resolution
# 2. Move these files to your ephys root directory.
#
# Note that the higher resolution (i.e., lower number) files are quite large when loaded. Depending on the python environment, the terminal may be killed when loading so much information into memory.

resolution = 100
from element_interface.utils import find_full_path
from workflow_array_ephys.paths import get_ephys_root_data_dir
nrrd_filepath = find_full_path(get_ephys_root_data_dir(), 
                               f'annotation_{resolution}.nrrd')
ontology_csv_filepath = find_full_path(get_ephys_root_data_dir(), 'query.csv')

# Next, we'll load annotation information from the files above to generate a set of lookup tables for the entire brain volume.

from workflow_array_ephys.localization import coordinate_framework as ccf
from element_electrode_localization.coordinate_framework import load_ccf_annotation
load_ccf_annotation(
    ccf_id=n, version_name='ccf_2017', voxel_resolution=resolution,
    nrrd_filepath=nrrd_filepath,
    ontology_csv_filepath=ontology_csv_filepath)

from workflow_array_ephys.localization import coordinate_framework as ccf
ccf.BrainRegionAnnotation()


ccf.BrainRe
