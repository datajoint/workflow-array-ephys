# DataJoint Workflow - Array Electrophysiology

Workflow for extracellular array electrophysiology data acquired with a polytrode probe
(e.g. [Neuropixels](https://www.neuropixels.org), Neuralynx) using the [SpikeGLX](https://github.com/billkarsh/SpikeGLX) or
[OpenEphys](https://open-ephys.org/gui) acquisition software and processed with [MATLAB-based Kilosort](https://github.com/MouseLand/Kilosort) or [python-based Kilosort](https://github.com/MouseLand/pykilosort) spike sorting software.

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
4. Export of `no_curation` schema to NWB and DANDI (see [notebooks/09-NWB-export.ipynb](notebooks/09-NWB-export.ipynb)).

See the [Element Array Electrophysiology documentation](https://elements.datajoint.org/description/array_ephys/) for the background information and development timeline.

For more information on the DataJoint Elements project, please visit <https://elements.datajoint.org>.  This work is supported by the National Institutes of Health.

## Workflow architecture

The electrophysiology workflow presented here uses components from 4 DataJoint Elements
([element-lab](https://github.com/datajoint/element-lab),
[element-animal](https://github.com/datajoint/element-animal),
[element-session](https://github.com/datajoint/element-session),
[element-array-ephys](https://github.com/datajoint/element-array-ephys)) assembled
together to form a fully functional workflow. Note that element-array-ephys offers three
schema options, selected via the DataJoint config file, with
`dj.config['custom']['ephys_mode']`

+ `acute` probe insertion, with curated clustering
+ `chronic` probe insertion, with curated clustering
+ `no-curation`, acute probe insertion with kilosort triggered clustering and supported NWB export
+ `precluster`, acute probe insertion with pre-processing steps prior to clustering and curated clustering

![](https://raw.githubusercontent.com/datajoint/workflow-array-ephys/main/images/attached_array_ephys_element.svg)

Optionally, this can be used in conjunction with
[element-event](https://github.com/datajoint/element-event)
and [element-electrode-localization](https://github.com/datajoint/element-electrode-localization/).

![](https://raw.githubusercontent.com/datajoint/workflow-array-ephys/main/images/attached_trial_analysis.svg)

![](https://raw.githubusercontent.com/datajoint/workflow-array-ephys/main/images/attached_electrode_localization.svg)

## Installation instructions

The installation instructions can be found at the
[DataJoint Elements documentation](https://elements.datajoint.org/usage/install/).

## Interacting with the DataJoint workflow

Please refer to the workflow-specific
[Jupyter notebooks](/notebooks)
for an in-depth explanation of how to ...

1. Run the workflow ([03-process.ipynb](notebooks/03-process.ipynb)).
2. Explore the data ([05-explore.ipynb](notebooks/05-explore.ipynb)).
3. Examine trialized analyses, and establish downstream analyses
([07-downstream-analysis.ipynb](notebooks/07-downstream-analysis.ipynb))
4. Locate probes within the
[Common Coordinate Framework](https://www.sciencedirect.com/science/article/pii/S0092867420304025)
([08-electrode-localization.ipynb](notebooks/08-electrode-localization.ipynb))
5. Export to NWB and DANDI ([09-NWB-export.ipynb](notebooks/09-NWB-export.ipynb))

See our YouTube tutorial for a walkthrough of the schemas and functions:
  [![YouTube tutorial](https://img.youtube.com/vi/KQlGYOBq7ow/0.jpg)](https://www.youtube.com/watch?v=KQlGYOBq7ow)

## Citation

If your work uses DataJoint and DataJoint Elements, please cite the respective Research Resource Identifiers (RRIDs) and manuscripts.


* DataJoint for Python or MATLAB
  + Yatsenko D, Reimer J, Ecker AS, Walker EY, Sinz F, Berens P, Hoenselaar A, Cotton RJ, Siapas AS, Tolias AS. DataJoint: managing big scientific data using MATLAB or Python. bioRxiv. 2015 Jan 1:031658. doi: <https://doi.org/10.1101/031658>

  + DataJoint ([RRID:SCR_014543](https://scicrunch.org/resolver/SCR_014543)) - DataJoint for `<Select Python or MATLAB>` (version `<Enter version number>`)

+ DataJoint Elements
  + Yatsenko D, Nguyen T, Shen S, Gunalan K, Turner CA, Guzman R, Sasaki M, Sitonic D, Reimer J, Walker EY, Tolias AS. DataJoint Elements: Data Workflows for Neurophysiology. bioRxiv. 2021 Jan 1. doi: <https://doi.org/10.1101/2021.03.30.437358>

  + DataJoint Elements ([RRID:SCR_021894](https://scicrunch.org/resolver/SCR_021894)) - Element Array Electrophysiology (version `<Enter version number>`)
