# run all tests:
# pytest -sv --cov-report term-missing --cov=workflow_array_ephys -p no:warnings tests/
# run one test, debug:
# pytest [above options] --pdb tests/tests_name.py -k function_name

import os
import sys
import pytest
import pandas as pd
import pathlib
import datajoint as dj

from workflow_array_ephys.paths import get_ephys_root_data_dir
from element_interface.utils import find_full_path


# ------------------- SOME CONSTANTS -------------------

_tear_down = False
verbose = False

test_user_data_dir = pathlib.Path('./tests/user_data')
test_user_data_dir.mkdir(exist_ok=True)

sessions_dirs = ['subject1/session1',
                 'subject2/session1',
                 'subject2/session2',
                 'subject3/session1',
                 'subject4/experiment1',
                 'subject5/session1',
                 'subject6/session1']

# --------------------  HELPER CLASS --------------------


class QuietStdOut:
    """If verbose set to false, used to quiet tear_down table.delete prints"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# ---------------------- FIXTURES ----------------------


@pytest.fixture(autouse=True)
def dj_config():
    """ If dj_local_config exists, load"""
    if pathlib.Path('./dj_local_conf.json').exists():
        dj.config.load('./dj_local_conf.json')
    dj.config['safemode'] = False
    dj.config['custom'] = {
        'ephys_mode': (os.environ.get('EPHYS_MODE')
                       or dj.config['custom']['ephys_mode']),
        'database.prefix': (os.environ.get('DATABASE_PREFIX')
                            or dj.config['custom']['database.prefix']),
        'ephys_root_data_dir': (os.environ.get('EPHYS_ROOT_DATA_DIR').split(',') if os.environ.get('EPHYS_ROOT_DATA_DIR') else dj.config['custom']['ephys_root_data_dir'])
    }
    return


@pytest.fixture(autouse=True)
def test_data(dj_config):
    """If data does not exist or partial data is present,
    attempt download with DJArchive to the first listed root directory"""
    test_data_exists = True
    for p in sessions_dirs:
        try:
            find_full_path(get_ephys_root_data_dir(), p)
        except FileNotFoundError:
            test_data_exists = False   # If data not found

    if not test_data_exists:           # attempt to djArchive dowload
        try:
            dj.config['custom'].update({
                'djarchive.client.endpoint':
                    os.environ['DJARCHIVE_CLIENT_ENDPOINT'],
                'djarchive.client.bucket':
                    os.environ['DJARCHIVE_CLIENT_BUCKET'],
                'djarchive.client.access_key':
                    os.environ['DJARCHIVE_CLIENT_ACCESSKEY'],
                'djarchive.client.secret_key':
                    os.environ['DJARCHIVE_CLIENT_SECRETKEY']
            })
        except KeyError as e:
            raise FileNotFoundError(
                f' Full test data not available.'
                f'\nAttempting to download from DJArchive,'
                f' but no credentials found in environment variables.'
                f'\nError: {str(e)}')

        import djarchive_client
        client = djarchive_client.client()

        test_data_dir = get_ephys_root_data_dir()
        if isinstance(test_data_dir, list):  # if multiple root dirs, first
            test_data_dir = test_data_dir[0]

        client.download('workflow-array-ephys-benchmark',
                        'v2',
                        str(test_data_dir), create_target=False)
    return


@pytest.fixture
def pipeline():
    from workflow_array_ephys import pipeline
    yield {'subject': pipeline.subject,
           'lab': pipeline.lab,
           'ephys': pipeline.ephys,
           'probe': pipeline.probe,
           'session': pipeline.session,
           'get_ephys_root_data_dir': pipeline.get_ephys_root_data_dir,
           'ephys_mode': pipeline.ephys_mode}

    if verbose and _tear_down:
        pipeline.subject.Subject.delete()
    elif not verbose and _tear_down:
        with QuietStdOut():
            pipeline.subject.Subject.delete()


@pytest.fixture
def subjects_csv():
    """ Create a 'subjects.csv' file"""
    input_subjects = pd.DataFrame(columns=['subject', 'sex',
                                           'subject_birth_date',
                                           'subject_description'])
    input_subjects.subject = ['subject1', 'subject2',
                              'subject3', 'subject4',
                              'subject5', 'subject6']
    input_subjects.sex = ['F', 'M', 'M', 'M', 'F', 'F']
    input_subjects.subject_birth_date = ['2020-01-01 00:00:01',
                                         '2020-01-01 00:00:01',
                                         '2020-01-01 00:00:01',
                                         '2020-01-01 00:00:01',
                                         '2020-01-01 00:00:01',
                                         '2020-01-01 00:00:01']
    input_subjects.subject_description = ['dl56', 'SC035', 'SC038',
                                          'oe_talab', 'rich', 'manuel']
    input_subjects = input_subjects.set_index('subject')

    subjects_csv_path = pathlib.Path('./tests/user_data/subjects.csv')
    input_subjects.to_csv(subjects_csv_path)    # write csv file

    yield input_subjects, subjects_csv_path

    subjects_csv_path.unlink()                  # delete csv file after use


@pytest.fixture
def ingest_subjects(pipeline, subjects_csv):
    from workflow_array_ephys.ingest import ingest_subjects
    _, subjects_csv_path = subjects_csv
    ingest_subjects(subjects_csv_path, verbose=verbose)
    return


@pytest.fixture
def sessions_csv(test_data):
    """ Create a 'sessions.csv' file"""
    input_sessions = pd.DataFrame(columns=['subject', 'session_dir'])
    input_sessions.subject = ['subject1', 'subject2', 'subject2',
                              'subject3', 'subject4', 'subject5',
                              'subject6']
    input_sessions.session_dir = sessions_dirs
    input_sessions = input_sessions.set_index('subject')

    sessions_csv_path = pathlib.Path('./tests/user_data/sessions.csv')
    input_sessions.to_csv(sessions_csv_path)  # write csv file

    yield input_sessions, sessions_csv_path

    sessions_csv_path.unlink()  # delete csv file after use


@pytest.fixture
def ingest_sessions(ingest_subjects, sessions_csv):
    from workflow_array_ephys.ingest import ingest_sessions
    _, sessions_csv_path = sessions_csv
    ingest_sessions(sessions_csv_path, verbose=verbose)
    return


@pytest.fixture
def testdata_paths():
    """ Paths for test data 'subjectX/sessionY/probeZ/etc'"""
    return {
        'npx3A-p1-ks': 'subject5/session1/probe_1/ks2.1_01',
        'npx3A-p2-ks': 'subject5/session1/probe_2/ks2.1_01',
        'oe_npx3B-ks': 'subject4/experiment1/recording1/continuous/'
                       + 'Neuropix-PXI-100.0/ks',
        'sglx_npx3A-p1': 'subject5/session1/probe_1',
        'oe_npx3B': 'subject4/experiment1/recording1/continuous/'
                    + 'Neuropix-PXI-100.0',
        'sglx_npx3B-p1': 'subject6/session1/towersTask_g0_imec0',
        'npx3B-p1-ks': 'subject6/session1/towersTask_g0_imec0'
    }

@pytest.fixture
def ephys_insertionlocation(pipeline, ingest_sessions):
    """Insert probe location into ephys.InsertionLocation"""
    ephys = pipeline['ephys']
    
    for probe_insertion_key in ephys.ProbeInsertion.fetch('KEY'):
        ephys.InsertionLocation.insert1(dict(**probe_insertion_key,
                                             skull_reference='Bregma',
                                             ap_location=0,
                                             ml_location=0,
                                             depth=0,
                                             theta=0,
                                             phi=0,
                                             beta=0))
    yield

    if _tear_down:
        if verbose:
            ephys.InsertionLocation.delete()
        else:
            with QuietStdOut():
                ephys.InsertionLocation.delete()

@pytest.fixture
def kilosort_paramset(pipeline):
    """Insert kilosort parameters into ephys.ClusteringParamset"""
    ephys = pipeline['ephys']

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

    # Insert here, since most of the test will require this paramset inserted
    ephys.ClusteringParamSet.insert_new_params(
        clustering_method='kilosort2.5',
        paramset_desc='Spike sorting using Kilosort2.5',
        params=params_ks,
        paramset_idx=0)

    yield params_ks

    if _tear_down:
        if verbose:
            (ephys.ClusteringParamSet & 'paramset_idx = 0').delete()
        else:
            with QuietStdOut():
                (ephys.ClusteringParamSet & 'paramset_idx = 0').delete()


@pytest.fixture
def ephys_recordings(pipeline, ingest_sessions):
    """Populate ephys.EphysRecording"""
    ephys = pipeline['ephys']

    ephys.EphysRecording.populate()

    yield

    if _tear_down:
        if verbose:
            ephys.EphysRecording.delete()
        else:
            with QuietStdOut():
                ephys.EphysRecording.delete()


@pytest.fixture
def clustering_tasks(pipeline, kilosort_paramset, ephys_recordings):
    """Insert keys from ephys.EphysRecording into ephys.Clustering"""
    ephys = pipeline['ephys']

    for ephys_rec_key in (ephys.EphysRecording - ephys.ClusteringTask).fetch('KEY'):
        ephys_file_path = pathlib.Path(((ephys.EphysRecording.EphysFile & ephys_rec_key
                                         ).fetch('file_path'))[0])
        ephys_file = find_full_path(get_ephys_root_data_dir(), ephys_file_path)
        recording_dir = ephys_file.parent
        kilosort_dir = next(recording_dir.rglob('spike_times.npy')).parent
        ephys.ClusteringTask.insert1({**ephys_rec_key,
                                      'paramset_idx': 0,
                                      'task_mode': 'load',
                                      'clustering_output_dir': kilosort_dir.as_posix()},
                                     skip_duplicates=True)

    yield

    if _tear_down:
        if verbose:
            ephys.ClusteringTask.delete()
        else:
            with QuietStdOut():
                ephys.ClusteringTask.delete()


@pytest.fixture
def clustering(clustering_tasks, pipeline):
    """Populate ephys.Clustering"""
    ephys = pipeline['ephys']

    ephys.Clustering.populate()

    yield

    if _tear_down:
        if verbose:
            ephys.Clustering.delete()
        else:
            with QuietStdOut():
                ephys.Clustering.delete()


@pytest.fixture
def curations(clustering, pipeline):
    ephys_mode = pipeline['ephys_mode']

    if ephys_mode == 'no-curation':
        yield
    else:
        ephys = pipeline['ephys']

        for key in (ephys.ClusteringTask - ephys.Curation).fetch('KEY'):
            ephys.Curation().create1_from_clustering_task(key)

        yield

        if _tear_down:
            if verbose:
                ephys.Curation.delete()
            else:
                with QuietStdOut():
                    ephys.Curation.delete()
