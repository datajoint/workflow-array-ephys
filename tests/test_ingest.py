import pathlib

from workflow_ephys.ingest import (ingest_subjects, ingest_sessions)
from workflow_ephys.pipeline import (subject, lab, ephys, probe, Session,
                                     get_ephys_root_data_dir)

from . import subjects_csv, sessions_csv, kilosort_paramset


def test_ingest_subjects(subjects_csv):
    ingest_subjects()
    assert len(subject.Subject()) == 5


def test_ingest_sessions(sessions_csv):
    ingest_sessions()
    assert len(Session()) == 6
    assert len(probe.Probe()) == 8
    assert len(ephys.ProbeInsertion()) == 12

    sess = sessions_csv.iloc[0]
    sess_dir = pathlib.Path(sess.session_dir).relative_to(get_ephys_root_data_dir())
    assert (Session.Directory & {'subject': sess.subject}).fetch1('session_dir') == sess_dir.as_posix()


def test_paramset_insert(kilosort_paramset):
    from elements_ephys.ephys import dict_to_uuid

    method, desc, paramset_hash = (ephys.ClusteringParamSet & {'paramset_idx': 0}).fetch1(
        'clustering_method', 'paramset_desc', 'param_set_hash')
    assert method == 'kilosort2'
    assert desc == 'Spike sorting using Kilosort2'
    assert dict_to_uuid(kilosort_paramset) == paramset_hash

