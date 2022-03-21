# DataJoint Workflow - Array Electrophysiology

Workflow for extracellular array electrophysiology data acquired with a polytrode probe (e.g.
Neuropixels, Neuralynx) using the `SpikeGLX` or `OpenEphys` acquisition software and processed
with MATLAB- or python-based `Kilosort` spike sorting software.

A complete electrophysiology workflow can be built using the DataJoint Elements.
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-array-ephys](https://github.com/datajoint/element-array-ephys)
+ Optionally, [element-event](https://github.com/datajoint/element-event)

This repository provides demonstrations for:
1. Set up a workflow using DataJoint Elements (see
[workflow_array_ephys/pipeline.py](workflow_array_ephys/pipeline.py))
2. Ingestion of data/metadata based on a predefined file structure, file naming
convention, and directory lookup methods (see
[workflow_array_ephys/paths.py](workflow_array_ephys/paths.py)).
3. Ingestion of clustering results.
4. Ingestion of experimental condition information and downstream [PSTH analysis](https://www.sciencedirect.com/topics/neuroscience/peristimulus-time-histogram).

## Workflow architecture

The electrophysiology workflow presented here uses components from 5 DataJoint 
Elements (`element-lab`, `element-animal`, `element-session`, `element-event`,
`element-array-ephys`) assembled together to form a fully functional workflow.

### element-lab

![element-lab](
https://github.com/datajoint/element-lab/raw/main/images/lab_diagram.svg)

### element-animal

![element-animal](
https://github.com/datajoint/element-animal/raw/main/images/subject_diagram.svg)

### assembled with element-array-ephys

![element-array-ephys](images/attached_array_ephys_element.svg)

### assembled with element-event and workflow analysis

![worklow-trial-analysis](attached_trial_analysis.svg)

## Installation instructions

+ The installation instructions can be found at the 
[datajoint-elements repository](https://github.com/datajoint/datajoint-elements/blob/main/gh-pages/docs/install.md).

## Interacting with the DataJoint workflow

Please refer to the following workflow-specific 
 [Jupyter notebooks](/notebooks) for an in-depth explanation of how to ...
+ run the workflow ([03-process.ipynb](notebooks/03-process.ipynb)) 
+ explore the data ([05-explore.ipynb](notebooks/05-explore.ipynb))
+ visualize trial-based analyses ([07-downstream-analysis.ipynb](notebooks/07-downstream-analysis.ipynb))
