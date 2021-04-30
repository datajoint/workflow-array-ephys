# Pipeline for extracellular electrophysiology using Neuropixels probe and kilosort clustering method

Build a full ephys pipeline using the canonical pipeline elements
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-array-ephys](https://github.com/datajoint/element-array-ephys)

This repository provides demonstrations for:
1. Set up a workflow using different elements (see [workflow_array_ephys/pipeline.py](workflow_array_ephys/pipeline.py))
2. Ingestion of data/metadata based on:
    + predefined file/folder structure and naming convention
    + predefined directory lookup methods (see [workflow_array_ephys/paths.py](workflow_array_ephys/paths.py))
3. Ingestion of clustering results (built-in routine from the ephys element)


## Pipeline Architecture

The electrophysiology pipeline presented here uses pipeline components from 4 DataJoint Elements,
`element-lab`, `element-animal`, `element-session` and `element-array-ephys`, assembled together to form a fully functional workflow.

### element-lab

![element-lab](https://github.com/datajoint/element-lab/raw/main/images/element_lab_diagram.svg)

### element-animal

![element-animal](https://github.com/datajoint/element-animal/blob/main/images/subject_diagram.svg)

### assembled with element-array-ephys

![element-array-ephys](images/attached_array_ephys_element.svg)

## Installation instruction

### Step 1 - clone this project

Clone this repository from [here](https://github.com/datajoint/workflow-array-ephys)

+ Launch a new terminal and change directory to where you want to clone the repository to
    ```
    cd C:/Projects
    ```
+ Clone the repository:
    ```
    git clone https://github.com/datajoint/workflow-array-ephys
    ```
+ Change directory to `workflow-array-ephys`
    ```
    cd workflow-array-ephys
    ```

### Step 2 - Setup virtual environment
It is highly recommended (though not strictly required) to create a virtual environment to run the pipeline.

+ You can install with `virtualenv` or `conda`.  Below are the commands for `virtualenv`.

+ If `virtualenv` not yet installed, run `pip install --user virtualenv`

+ To create a new virtual environment named `venv`:
    ```
    virtualenv venv
    ```

+ To activated the virtual environment:
    + On Windows:
        ```
        .\venv\Scripts\activate
        ```

    + On Linux/macOS:
        ```
        source venv/bin/activate
        ```

### Step 3 - Install this repository

From the root of the cloned repository directory:
    ```
    pip install -e .
    ```

Note: the `-e` flag will install this repository in editable mode,
in case there's a need to modify the code (e.g. the `pipeline.py` or `paths.py` scripts).
If no such modification required, using `pip install .` is sufficient

### Step 4 - Jupyter Notebook
+ Register an IPython kernel with Jupyter
    ```
    ipython kernel install --name=workflow-array-ephys
    ```

### Step 5 - Configure the `dj_local_conf.json`

We provided a tutorial notebook [01-configuration](notebooks/01-configuration.ipynb) to guide the configuration.

At the root of the repository folder,
create a new file `dj_local_conf.json` with the following template:

```json
{
  "database.host": "<hostname>",
  "database.user": "<username>",
  "database.password": "<password>",
  "loglevel": "INFO",
  "safemode": true,
  "display.limit": 7,
  "display.width": 14,
  "display.show_tuple_count": true,
  "custom": {
      "database.prefix": "<neuro_>",
      "ephys_root_data_dir": "<C:/data/ephys_root_data_dir>"
    }
}
```

+ Specify database's `hostname`, `username`, and `password` properly.

+ Specify a `database.prefix` to create the schemas.

+ Setup your data directory (`ephys_root_data_dir`) following the convention described below.


### Installation complete

+ At this point the setup of this workflow is complete.

## Directory structure and file naming convention

The workflow presented here is designed to work with the directory structure and file naming convention as followed

+ The `ephys_root_data_dir` is configurable in the `dj_local_conf.json`, under `custom/ephys_root_data_dir` variable

+ The `subject` directory names must match the identifiers of your subjects in the [subjects.csv](./user_data/subjects.csv) script

+ The `session` directories can have any naming convention

+ Each session can have multiple probes, the `probe` directories must match the following naming convention:

    `*[0-9]` (where `[0-9]` is a one digit number specifying the probe number)

+ Each `probe` directory should contain:

    + One neuropixels meta file, with the following naming convention:

        `*[0-9].ap.meta`

    + Potentially one Kilosort output folder

```
root_data_dir/
└───subject1/
│   └───session0/
│   │   └───imec0/
│   │   │   │   *imec0.ap.meta
│   │   │   └───ksdir/
│   │   │       │   spike_times.npy
│   │   │       │   templates.npy
│   │   │       │   ...
│   │   └───imec1/
│   │       │   *imec1.ap.meta
│   │       └───ksdir/
│   │           │   spike_times.npy
│   │           │   templates.npy
│   │           │   ...
│   └───session1/
│   │   │   ...
└───subject2/
│   │   ...
```

We provide an example data set to run through this workflow. The instruction of data downloading is in the notebook [00-data-download](notebooks/00-data-download-optional.ipynb).


## Running this workflow

For new users, we recommend using the following two notebooks to run through the workflow.
+ [03-process](notebooks/03-process.ipynb)
+ [04-automate](notebooks/04-automate-optional.ipynb)

Here is a general instruction:

Once you have your data directory configured with the above convention,
populating the pipeline with your data amounts to these 3 steps:

1. Insert meta information (e.g. subjects, sessions, etc.) - modify:
    + user_data/subjects.csv
    + user_data/sessions.csv

2. Import session data - run:
    ```
    python workflow_array_ephys/ingest.py
    ```

3. Import clustering data and populate downstream analyses - run:
    ```
    python workflow_array_ephys/populate.py
    ```

+ For inserting new subjects, sessions or new analysis parameters, step 1 needs to be re-executed.

+ Rerun step 2 and 3 every time new sessions or clustering data become available.

+ In fact, step 2 and 3 can be executed as scheduled jobs that will automatically process any data newly placed into the `imaging_root_data_dir`.

## Interacting with the DataJoint pipeline and exploring data

For new users, we recommend using our notebook [05-explore](notebooks/05-explore.ipynb) to interact with the pipeline.

Here is a general instruction:


+ Connect to database and import tables
    ```
    from workflow_array_ephys.pipeline import *
    ```

+ View ingested/processed data
    ```
    subject.Subject()
    session.Session()
    ephys.ProbeInsertion()
    ephys.EphysRecording()
    ephys.Clustering()
    ephys.Clustering.Unit()
    ```

+ If required to drop all schemas, the following is the dependency order. Also refer to [06-drop](notebooks/06-drop-optional.ipynb)
    ```
    from workflow_array_ephys.pipeline import *

    ephys.schema.drop()
    probe.schema.drop()
    session.schema.drop()
    subject.schema.drop()
    lab.schema.drop()
    ```


## Developer Guide

### Development mode installation

This method allows you to modify the source code for `workflow-array-ephys`, `element-array-ephys`, `element-animal`, `element-session`, and `element-lab`.

+ Launch a new terminal and change directory to where you want to clone the repositories
    ```
    cd C:/Projects
    ```
+ Clone the repositories
    ```
    git clone https://github.com/datajoint/element-lab
    git clone https://github.com/datajoint/element-animal
    git clone https://github.com/datajoint/element-session
    git clone https://github.com/datajoint/element-array-ephys
    git clone https://github.com/datajoint/workflow-array-ephys
    ```
+ Install each package with the `-e` option
    ```
    pip install -e ./workflow-array-ephys
    pip install -e ./element-session
    pip install -e ./element-lab
    pip install -e ./element-animal
    pip install -e ./element-array-ephys
    ```

### Running tests

1. Download the test dataset to your local machine
(note the directory where the dataset is saved at - e.g. `/tmp/testset`)

2. Create an `.env` file with the following content:

    > TEST_DATA_DIR=/tmp/testset

    (replace `/tmp/testset` with the directory where you have the test dataset downloaded to)

3. Run:


    docker-compose -f docker-compose-test.yaml up --build
