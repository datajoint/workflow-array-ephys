# DataJoint Workflow - Array Electrophysiology

Workflow for extracellular array electrophysiology data acquired with a polytrode probe (e.g.
Neuropixels, Neuralynx) using the `SpikeGLX` or `OpenEphys` acquisition software and processed
with MATLAB- or python-based `Kilosort` spike sorting software.

A complete electrophysiology workflow can be built using the DataJoint Elements.
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-array-ephys](https://github.com/datajoint/element-array-ephys)

This repository provides demonstrations for:
1. Set up a workflow using DataJoint Elements (see
[workflow_array_ephys/pipeline.py](workflow_array_ephys/pipeline.py))
2. Ingestion of data/metadata based on a predefined file structure, file naming
convention, and directory lookup methods (see
[workflow_array_ephys/paths.py](workflow_array_ephys/paths.py)).
3. Ingestion of clustering results.

For more information on the DataJoint Elements project, please visit https://elements.datajoint.org.  This work is supported by the National Institutes of Health.

## Workflow architecture

The electrophysiology workflow presented here uses components from 4 DataJoint 
Elements ([element-lab](https://github.com/datajoint/element-lab), 
[element-animal](https://github.com/datajoint/element-animal), 
[element-session](https://github.com/datajoint/element-session),
[element-array-ephys](https://github.com/datajoint/element-array-ephys)) 
assembled together to form a fully functional workflow.

![element-array-ephys](images/attached_array_ephys_element.svg)

## Installation instructions

+ The installation instructions can be found at the 
[DataJoint Elements documentation](https://elements.datajoint.org/usage/install/).

## Interacting with the DataJoint workflow

+ Please refer to the following workflow-specific 
 [Jupyter notebooks](/notebooks) for an in-depth explanation of how to run the 
 workflow ([03-process.ipynb](notebooks/03-process.ipynb)) and explore the data 
 ([05-explore.ipynb](notebooks/05-explore.ipynb)).

## Citation

+ If your work uses DataJoint and DataJoint Elements, please cite the respective Research Resource Identifiers (RRIDs) and manuscripts.

+ DataJoint for Python or MATLAB
    + Yatsenko D, Reimer J, Ecker AS, Walker EY, Sinz F, Berens P, Hoenselaar A, Cotton RJ, Siapas AS, Tolias AS. DataJoint: managing big scientific data using MATLAB or Python. bioRxiv. 2015 Jan 1:031658. doi: https://doi.org/10.1101/031658

    + DataJoint ([RRID:SCR_014543](https://scicrunch.org/resolver/SCR_014543)) - DataJoint for < Python or MATLAB > (version < enter version number >)

+ DataJoint Elements
    + Yatsenko D, Nguyen T, Shen S, Gunalan K, Turner CA, Guzman R, Sasaki M, Sitonic D, Reimer J, Walker EY, Tolias AS. DataJoint Elements: Data Workflows for Neurophysiology. bioRxiv. 2021 Jan 1. doi: https://doi.org/10.1101/2021.03.30.437358

    + DataJoint Elements ([RRID:SCR_021894](https://scicrunch.org/resolver/SCR_021894)) - Element Array Electrophysiology (version < enter version number >)