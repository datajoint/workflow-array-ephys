from . import dj_config


def test_generate_pipeline():
    from workflow_ephys.pipeline import subject, lab, ephys, probe, Session

    subject_tbl, *_ = Session.parents(as_objects=True)

    # test elements connection from lab, subject to Session
    assert subject_tbl.full_table_name == subject.Subject.full_table_name

    # test elements connection from Session to probe, ephys
    session_tbl, probe_tbl = ephys.ProbeInsertion.parents(as_objects=True)
    assert session_tbl.full_table_name == Session.full_table_name
    assert probe_tbl.full_table_name == probe.Probe.full_table_name
    assert 'spike_times' in ephys.CuratedClustering.Unit.heading.secondary_attributes
