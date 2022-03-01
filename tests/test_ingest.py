import sys
import pathlib

from . import (dj_config, pipeline, test_data,
               subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, kilosort_paramset,
               ephys_recordings, clustering_tasks, clustering, curations)

# Set all to pass linter warning: PEP8 F811
__all__ = ['dj_config', 'pipeline', 'test_data', 'subjects_csv', 'ingest_subjects',
           'sessions_csv', 'ingest_sessions', 'testdata_paths', 'kilosort_paramset',
           'ephys_recordings', 'clustering_tasks', 'clustering', 'curations']


def test_ingest_subjects(pipeline, ingest_subjects):
    """ Check number of subjects inserted into the `subject.Subject` table """
    subject = pipeline['subject']
    assert len(subject.Subject()) == 6


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    ephys = pipeline['ephys']
    probe = pipeline['probe']
    session = pipeline['session']

    assert len(session.Session()) == 7
    assert len(probe.Probe()) == 9
    assert len(ephys.ProbeInsertion()) == 13

    sessions, _ = sessions_csv
    sess = sessions.iloc[0]

    assert (session.SessionDirectory
            & {'subject': sess.name}).fetch1('session_dir') == sess.session_dir


def test_find_valid_full_path(pipeline, sessions_csv):
    from element_interface.utils import find_full_path

    get_ephys_root_data_dir = pipeline['get_ephys_root_data_dir']
    ephys_root_data_dir = ([get_ephys_root_data_dir()]
                           if not isinstance(get_ephys_root_data_dir(), list)
                           else get_ephys_root_data_dir())

    # add more options for root directories
    if sys.platform == 'win32':  # win32 even if Windows 64-bit
        ephys_root_data_dir = ephys_root_data_dir + ['J:/', 'M:/']
    else:
        ephys_root_data_dir = ephys_root_data_dir + ['mnt/j', 'mnt/m']

    # test: providing relative-path: correctly search for the full-path
    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    session_full_path = find_full_path(ephys_root_data_dir, sess.session_dir)

    docker_full_path = pathlib.Path('/main/test_data/workflow_ephys_data1/'
                                    + 'subject1/session1')

    assert docker_full_path == session_full_path, str('Session path does not match '
                                                      + 'docker root: '
                                                      + f'{docker_full_path}')


def test_find_root_directory(pipeline, sessions_csv):
    """
    Test that ephys_root_data_dir loaded as docker directory
        /main/test_data/workflow_ephys_data1/
    """
    from element_interface.utils import find_root_directory

    get_ephys_root_data_dir = pipeline['get_ephys_root_data_dir']
    ephys_root_data_dir = ([get_ephys_root_data_dir()]
                           if not isinstance(get_ephys_root_data_dir(), list)
                           else get_ephys_root_data_dir())
    # add more options for root directories
    if sys.platform == 'win32':
        ephys_root_data_dir = ephys_root_data_dir + ['J:/', 'M:/']
    else:
        ephys_root_data_dir = ephys_root_data_dir + ['mnt/j', 'mnt/m']

    # test: providing full-path: correctly search for the root_dir
    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    # set to /main/, will only work in docker environment
    session_full_path = pathlib.Path('/main/test_data/workflow_ephys_data1',
                                     sess.session_dir)
    root_dir = find_root_directory(ephys_root_data_dir, session_full_path)

    assert root_dir.as_posix() == '/main/test_data/workflow_ephys_data1',\
        'Root path does not match docker: /main/test_data/workflow_ephys_data1'


def test_paramset_insert(kilosort_paramset, pipeline):
    ephys = pipeline['ephys']
    from element_interface.utils import dict_to_uuid

    method, desc, paramset_hash = (ephys.ClusteringParamSet
                                   & {'paramset_idx': 0}).fetch1(
        'clustering_method', 'paramset_desc', 'param_set_hash')
    assert method == 'kilosort2'
    assert desc == 'Spike sorting using Kilosort2'
    assert dict_to_uuid(kilosort_paramset) == paramset_hash
