# Changelog

Observes [Semantic Versioning](https://semver.org/spec/v2.0.0.html) standard and
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) convention.

## [0.3.2] - 2023-04-14

+ Add - `quality_metrics.ipynb` for visualizing quality metrics.
+ Add - Documentation for attributes in `ephys.QualityMetrics.Waveform`.
+ Update - pytest for `ephys.QualityMetrics.populate`.

## [0.3.1] - 2023-04-12

+ Add - pytest for new `QCmetric` tables.
+ Add - `graphviz` in `requirements.txt`.
+ Update - visualization notebook.

## [0.3.0] - 2023-03-09

+ Add - Demo notebooks and capabilities using GitHub Codespaces
+ Add - pre-commit, markdown lint, and spell check config files
+ Update - Revise pytest and docker structure to streamline testing
+ Fix - `element-array-ephys` version error when installing via requirements.txt

## [0.2.6] - 2022-01-12

+ Update - Requirements to install main branch of `element-array-ephys`.
+ Add - Quality Metric plots to visualization notebook.

## [0.2.5] - 2022-01-03

+ Add - notebook 10 for figures and widget for ephys results.
+ Add - Test for `ephys_report` module.

## [0.2.4] - 2022-09-20

+ Add - Add [0.2.3] and revise [0.2.4] notebook for Allen Institute workshop

## [0.2.2] - 2022-09-18

+ Update - config ephys roots in notebooks for codebook deployment
+ Update - requirements.txt to add element electrode localization
+ Update - add lab.User insert to ingest.py for users with empty element-lab schemas

## [0.2.1] - 2022-07-22

+ Add - Mention CodeBook data directory in notebooks
+ Add - Mention of config items in notebook 09
+ Update - Remove directory assertion in notebooks for CodeBook deployment
+ Update - Move all export functions from `pipeline` to `export` script

## [0.2.0] - 2022-07-08

+ Add - Adopt black formatting into code base
+ Add - GitHub Issue templates
+ Add - Code of conduct
+ Add - Jupytext paired python scripts
+ Add - Example data for trials, events, blocks, recordings, and alignments
+ Add - Analysis schema
+ Add - Raster and PSTH plots
+ Add - Video tutorial link to README
+ Add - Images for README
+ Add - Jupyter notebooks for downstream analysis, electrode localization, and NWB export
+ Add - Electrode localization schema activation script
+ Update - README for ephys modes, element-event, and element-electrode-localization
+ Update - Docker and Compose files for element-event and element-electrode-localization
+ Update - Pipeline script for ephys mode and element-event
+ Update - Pytests

## [0.1.0] - 2022-06-02

+ Update - Docker and Compose files
+ Add - NWB export pytests

## 0.1.0a4 - 2022-01-21

+ Add - Create Docker and Compose files for active development.

## 0.1.0a3 - 2022-01-18

+ Update - Notebooks
+ Update - Move instructions to
  [datajoint-elements/install.md](https://github.com/datajoint/datajoint-elements/blob/main/install.md).
+ Update - Docker and Compose files for new base image and added options to install
  specific forks for tests.

## 0.1.0a2 - 2021-04-12

+ Update - Pytests
+ Update - Change version to reflect release phase.

## 0.1.1 - 2021-03-26

+ Add - Version

[0.3.2]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.3.2
[0.3.1]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.3.1
[0.3.0]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.3.0
[0.2.6]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.6
[0.2.5]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.5
[0.2.4]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.4
[0.2.3]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.3
[0.2.2]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.2
[0.2.1]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.1
[0.2.0]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.2.0
[0.1.0]: https://github.com/datajoint/workflow-array-ephys/releases/tag/0.1.0
