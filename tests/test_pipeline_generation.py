from . import dj_config, pipeline


def test_generate_pipeline(pipeline):
    subject = pipeline["subject"]
    ephys = pipeline["ephys"]
    probe = pipeline["probe"]
    session = pipeline["session"]

    # test elements connection from lab, subject to Session
    assert subject.Subject.full_table_name in session.Session.parents()

    # test elements connection from Session to probe, ephys
    assert session.Session.full_table_name in ephys.ProbeInsertion.parents()
    assert probe.Probe.full_table_name in ephys.ProbeInsertion.parents()
    assert "spike_times" in (ephys.CuratedClustering.Unit.heading.secondary_attributes)
