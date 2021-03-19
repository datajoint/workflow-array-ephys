import pathlib

from . import *


def test_ingest_subjects(pipeline, ingest_subjects):
    subject, _, _, _, _, _ = pipeline
    assert len(subject.Subject()) == 5


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    _, _, ephys, probe, Session, get_ephys_root_data_dir = pipeline
    assert len(Session()) == 6
    assert len(probe.Probe()) == 8
    assert len(ephys.ProbeInsertion()) == 12

    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    sess_dir = pathlib.Path(sess.session_dir).relative_to(get_ephys_root_data_dir())
    assert (Session.Directory & {'subject': sess.name}).fetch1('session_dir') == sess_dir.as_posix()


def test_paramset_insert(kilosort_paramset, pipeline):
    _, _, ephys, _, _, _ = pipeline
    from elements_ephys.ephys import dict_to_uuid

    method, desc, paramset_hash = (ephys.ClusteringParamSet & {'paramset_idx': 0}).fetch1(
        'clustering_method', 'paramset_desc', 'param_set_hash')
    assert method == 'kilosort2'
    assert desc == 'Spike sorting using Kilosort2'
    assert dict_to_uuid(kilosort_paramset) == paramset_hash

