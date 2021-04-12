import numpy as np

from . import (dj_config, pipeline,
               subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, kilosort_paramset,
               ephys_recordings, clustering_tasks, clustering, curations)


def test_ephys_recording_populate(pipeline, ephys_recordings):
    ephys = pipeline['ephys']
    assert len(ephys.EphysRecording()) == 12


def test_LFP_populate_npx3B_OpenEphys(testdata_paths, pipeline, ephys_recordings):
    ephys = pipeline['ephys']
    rel_path = testdata_paths['oe_npx3B']
    rec_key = (ephys.EphysRecording & (ephys.EphysRecording.EphysFile
                                       & f'file_path LIKE "%{rel_path}"')).fetch1('KEY')
    ephys.LFP.populate(rec_key)

    lfp_mean = (ephys.LFP & rec_key).fetch1('lfp_mean')
    assert len(lfp_mean) == 520054

    electrodes = (ephys.LFP.Electrode & rec_key).fetch('electrode')
    assert np.array_equal(
        electrodes,
        np.array([5,  14,  23,  32,  41,  50,  59,  68,  77,  86,  95, 104, 113,
                  122, 131, 140, 149, 158, 167, 176, 185, 194, 203, 212, 221, 230,
                  239, 248, 257, 266, 275, 284, 293, 302, 311, 320, 329, 338, 347,
                  356, 365, 374, 383]))


def test_LFP_populate_npx3A_SpikeGLX(testdata_paths, pipeline, ephys_recordings):
    ephys = pipeline['ephys']

    rel_path = testdata_paths['sglx_npx3A-p1']
    rec_key = (ephys.EphysRecording & (ephys.EphysRecording.EphysFile
                                       & f'file_path LIKE "%{rel_path}%"')).fetch1('KEY')
    ephys.LFP.populate(rec_key)

    lfp_mean = (ephys.LFP & rec_key).fetch1('lfp_mean')
    assert len(lfp_mean) == 846666

    electrodes = (ephys.LFP.Electrode & rec_key).fetch('electrode')
    assert np.array_equal(
        electrodes,
        np.array([5,  14,  23,  32,  41,  50,  59,  68,  77,  86,  95, 104, 113,
                  122, 131, 140, 149, 158, 167, 176, 185, 194, 203, 212, 221, 230,
                  239, 248, 257, 266, 275, 284, 293, 302, 311, 320, 329, 338, 347,
                  356, 365, 374, 383]))


def test_clustering_populate(clustering, pipeline):
    ephys = pipeline['ephys']
    assert len(ephys.Clustering()) == 12


def test_curated_clustering_populate(curations, pipeline, testdata_paths):
    ephys = pipeline['ephys']

    rel_path = testdata_paths['npx3A-p1-ks']
    curation_key = (ephys.Curation & f'curation_output_dir LIKE "%{rel_path}"').fetch1('KEY')
    ephys.CuratedClustering.populate(curation_key)
    assert len(ephys.CuratedClustering.Unit & curation_key
               & 'cluster_quality_label = "good"') == 76

    rel_path = testdata_paths['oe_npx3B-ks']
    curation_key = (ephys.Curation & f'curation_output_dir LIKE "%{rel_path}"').fetch1('KEY')
    ephys.CuratedClustering.populate(curation_key)
    assert len(ephys.CuratedClustering.Unit & curation_key
               & 'cluster_quality_label = "good"') == 68
