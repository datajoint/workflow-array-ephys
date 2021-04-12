import sys
import pathlib

from . import (dj_config, pipeline,
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
    sess_dir = pathlib.Path(sess.session_dir).relative_to(get_ephys_root_data_dir())
    assert (session.SessionDirectory
            & {'subject': sess.name}).fetch1('session_dir') == sess_dir.as_posix()


def test_find_valid_full_path(pipeline, sessions_csv):
    from element_array_ephys import find_valid_full_path

    get_ephys_root_data_dir = pipeline['get_ephys_root_data_dir']

    # add more options for root directories
    if sys.platform == 'win32':
        ephys_root_data_dir = [get_ephys_root_data_dir(), 'J:/', 'M:/']
    else:
        ephys_root_data_dir = [get_ephys_root_data_dir(), 'mnt/j', 'mnt/m']

    # test 1 - providing full-path: correctly search for the root_dir
    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    session_full_path = pathlib.Path(sess.session_dir)

    _, root_dir = find_valid_full_path(ephys_root_data_dir, session_full_path)

    assert root_dir == get_ephys_root_data_dir()

    # test 2 - providing relative-path: correctly search for the root_dir and full-path
    rel_path = pathlib.Path(session_full_path).relative_to(
        pathlib.Path(get_ephys_root_data_dir()))
    full_path, root_dir = find_valid_full_path(ephys_root_data_dir, rel_path)

    assert root_dir == get_ephys_root_data_dir()
    assert full_path == session_full_path


def test_paramset_insert(kilosort_paramset, pipeline):
    ephys = pipeline['ephys']
    from element_array_ephys.ephys import dict_to_uuid

    method, desc, paramset_hash = (ephys.ClusteringParamSet & {'paramset_idx': 0}).fetch1(
        'clustering_method', 'paramset_desc', 'param_set_hash')
    assert method == 'kilosort2'
    assert desc == 'Spike sorting using Kilosort2'
    assert dict_to_uuid(kilosort_paramset) == paramset_hash

