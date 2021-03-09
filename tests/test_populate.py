from workflow_ephys.pipeline import (subject, lab, ephys, probe, Session,
                                     get_ephys_root_data_dir)

from . import clustering_tasks, curations, testdata_paths


def test_ephys_recording_populate():
    ephys.EphysRecording.populate()
    assert len(ephys.EphysRecording()) == 12


def test_clustering_populate(clustering_tasks):
    ephys.Clustering.populate()
    assert len(ephys.Clustering()) == 12


def test_unit_populate(curations, testdata_paths):
    rel_path = testdata_paths['npx3A-p0-ks']
    curation_key = (ephys.Curation & f'curation_output_dir LIKE "%{rel_path}"').fetch1('KEY')
    ephys.Unit.populate(curation_key)
    assert len(ephys.Unit & curation_key & 'cluster_quality_label = "good"') == 76

    rel_path = testdata_paths['oe_npx3B-ks']
    curation_key = (ephys.Curation & f'curation_output_dir LIKE "%{rel_path}"').fetch1('KEY')
    ephys.Unit.populate(curation_key)
    assert len(ephys.Unit & curation_key & 'cluster_quality_label = "good"') == 68

