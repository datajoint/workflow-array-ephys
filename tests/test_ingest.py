import pathlib

from . import (dj_config, pipeline,
               subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, kilosort_paramset,
               ephys_recordings, clustering_tasks, clustering, curations)


def test_ingest_subjects(pipeline, ingest_subjects):
    subject = pipeline['subject']
    assert len(subject.Subject()) == 5


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    ephys = pipeline['ephys']
    probe = pipeline['probe']
    Session = pipeline['Session']
    get_ephys_root_data_dir = pipeline['get_ephys_root_data_dir']

    assert len(Session()) == 6
    assert len(probe.Probe()) == 8
    assert len(ephys.ProbeInsertion()) == 12

    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    sess_dir = pathlib.Path(sess.session_dir).relative_to(get_ephys_root_data_dir())
    assert (Session.Directory
            & {'subject': sess.name}).fetch1('session_dir') == sess_dir.as_posix()


def test_paramset_insert(kilosort_paramset, pipeline):
    ephys = pipeline['ephys']
    from elements_ephys.ephys import dict_to_uuid

    method, desc, paramset_hash = (ephys.ClusteringParamSet & {'paramset_idx': 0}).fetch1(
        'clustering_method', 'paramset_desc', 'param_set_hash')
    assert method == 'kilosort2'
    assert desc == 'Spike sorting using Kilosort2'
    assert dict_to_uuid(kilosort_paramset) == paramset_hash

