import sys
import pathlib

from . import (dj_config, pipeline, test_data,
               subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, kilosort_paramset,
               ephys_recordings, clustering_tasks, clustering, curations)


def test_ingest_subjects(pipeline, ingest_subjects):
    subject = pipeline['subject']
    assert len(subject.Subject()) == 6


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    ephys = pipeline['ephys']
    probe = pipeline['probe']
    session = pipeline['session']
    get_ephys_root_data_dir = pipeline['get_ephys_root_data_dir']

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

    # add more options for root directories
    if sys.platform == 'win32':
        ephys_root_data_dir = [get_ephys_root_data_dir(), 'J:/', 'M:/']
    else:
        ephys_root_data_dir = [get_ephys_root_data_dir(), 'mnt/j', 'mnt/m']

    # test: providing relative-path: correctly search for the full-path
    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    session_full_path = pathlib.Path(get_ephys_root_data_dir()) / sess.session_dir

    full_path = find_full_path(ephys_root_data_dir, sess.session_dir)

    assert full_path == session_full_path


def test_find_root_directory(pipeline, sessions_csv):
    from element_interface.utils import find_root_directory

    get_ephys_root_data_dir = pipeline['get_ephys_root_data_dir']

    # add more options for root directories
    if sys.platform == 'win32':
        ephys_root_data_dir = [get_ephys_root_data_dir(), 'J:/', 'M:/']
    else:
        ephys_root_data_dir = [get_ephys_root_data_dir(), 'mnt/j', 'mnt/m']

    # test: providing full-path: correctly search for the root_dir
    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    session_full_path = pathlib.Path(get_ephys_root_data_dir()) / sess.session_dir
    root_dir = find_root_directory(ephys_root_data_dir, session_full_path)

    assert root_dir.as_posix() == get_ephys_root_data_dir()


def test_paramset_insert(kilosort_paramset, pipeline):
    ephys = pipeline['ephys']
    from element_interface.utils import dict_to_uuid

    method, desc, paramset_hash = (ephys.ClusteringParamSet & {'paramset_idx': 0}).fetch1(
        'clustering_method', 'paramset_desc', 'param_set_hash')
    assert method == 'kilosort2'
    assert desc == 'Spike sorting using Kilosort2'
    assert dict_to_uuid(kilosort_paramset) == paramset_hash

