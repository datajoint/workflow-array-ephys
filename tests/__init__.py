import os
import pytest
import pandas as pd
import pathlib
import datajoint as dj


@pytest.fixture(autouse=True)
def dj_config():
    dj.config.load('./dj_local_conf.json')

    dj.config['custom'] = {
        'database.prefix': os.environ.get('DATABASE_PREFIX', dj.config['custom']['database.prefix']),
        'ephys_root_data_dir': os.environ.get('EPHYS_ROOT_DATA_DIR', dj.config['custom']['ephys_root_data_dir'])
    }
    return


@pytest.fixture
def subjects_csv():
    """ Create a 'subjects.csv' file"""
    input_subjects = pd.DataFrame(columns=['subject', 'sex', 'subject_birth_date', 'subject_description'])
    input_subjects.subject = ['subject1', 'subject2', 'subject3', 'subject4', 'subject5']
    input_subjects.sex = ['F', 'M', 'M', 'M', 'F']
    input_subjects.subject_birth_date = ['2020-01-01 00:00:01', '2020-01-01 00:00:01',
                                         '2020-01-01 00:00:01', '2020-01-01 00:00:01', '2020-01-01 00:00:01']
    input_subjects.subject_description = ['dl56', 'SC035', 'SC038', 'oe_talab', 'rich']

    subjects_csv_fp = pathlib.Path('./tests/user_data/subjects.csv')

    input_subjects.to_csv(subjects_csv_fp)  # write csv file

    yield input_subjects

    subjects_csv_fp.unlink()  # delete csv file after use


@pytest.fixture
def sessions_csv():
    """ Create a 'sessions.csv' file"""
    input_sessions = pd.DataFrame(columns = ['subject', 'session_dir'])
    input_sessions.subject = ['subject1',
                              'subject2',
                              'subject2',
                              'subject3',
                              'subject4',
                              'subject5']
    input_sessions.session_dir = [r'F:\U24\workflow_ephys_data\subject1\session1',
                                  r'F:\U24\workflow_ephys_data\subject2\session1',
                                  r'F:\U24\workflow_ephys_data\subject2\session2',
                                  r'F:\U24\workflow_ephys_data\subject3\session1',
                                  r'F:\U24\workflow_ephys_data\subject4\experiment1',
                                  r'F:\U24\workflow_ephys_data\subject5\2018-07-03_19-10-39']

    sessions_csv_fp = pathlib.Path('./tests/user_data/sessions.csv')

    input_sessions.to_csv(sessions_csv_fp)  # write csv file

    yield input_sessions

    sessions_csv_fp.unlink()  # delete csv file after use


@pytest.fixture
def testdata_paths():
    return {
        'npx3A-p0-ks': 'subject5/2018-07-03_19-10-39/probe_1/ks2.1_01',
        'npx3A-p1-ks': 'subject5/2018-07-03_19-10-39/probe_1/ks2.1_01',
        'oe_npx3B-ks': 'subject4/experiment1/recording1/continuous/Neuropix-PXI-100.0/ks',
        'npx3A-p0': 'subject5/2018-07-03_19-10-39/probe_1',
        'oe_npx3B': 'subject4/experiment1/recording1/continuous/Neuropix-PXI-100.0',
    }


@pytest.fixture
def kilosort_paramset():
    from workflow_ephys.pipeline import ephys

    params_ks = {
        "fs": 30000,
        "fshigh": 150,
        "minfr_goodchannels": 0.1,
        "Th": [10, 4],
        "lam": 10,
        "AUCsplit": 0.9,
        "minFR": 0.02,
        "momentum": [20, 400],
        "sigmaMask": 30,
        "ThPr": 8,
        "spkTh": -6,
        "reorder": 1,
        "nskip": 25,
        "GPU": 1,
        "Nfilt": 1024,
        "nfilt_factor": 4,
        "ntbuff": 64,
        "whiteningRange": 32,
        "nSkipCov": 25,
        "scaleproc": 200,
        "nPCs": 3,
        "useRAM": 0
    }

    # doing the insert here as well, since most of the test will require this paramset inserted
    ephys.ClusteringParamSet.insert_new_params(
        'kilosort2', 0, 'Spike sorting using Kilosort2', params_ks)

    yield params_ks

    with dj.config(safemode=False):
        ephys.ClusteringParamSet.delete()


@pytest.fixture
def clustering_tasks(kilosort_paramset):
    from workflow_ephys.pipeline import ephys, get_ephys_root_data_dir

    root_dir = pathlib.Path(get_ephys_root_data_dir())
    for ephys_rec_key in (ephys.EphysRecording - ephys.ClusteringTask).fetch('KEY'):
        ephys_file = root_dir / (ephys.EphysRecording.EphysFile & ephys_rec_key).fetch('file_path')[0]
        recording_dir = ephys_file.parent
        kilosort_dir = next(recording_dir.rglob('spike_times.npy')).parent
        ephys.ClusteringTask.insert1({**ephys_rec_key,
                                      'paramset_idx': 0,
                                      'clustering_output_dir': kilosort_dir.as_posix()})

    ephys.Clustering.populate()

    yield

    with dj.config(safemode=False):
        ephys.ClusteringTask.delete()


@pytest.fixture
def curations(clustering_tasks):
    from workflow_ephys.pipeline import ephys

    for key in (ephys.ClusteringTask - ephys.Curation).fetch('KEY'):
        ephys.Curation().create1_from_clustering_task(key)

    yield

    with dj.config(safemode=False):
        ephys.Curation.delete()
