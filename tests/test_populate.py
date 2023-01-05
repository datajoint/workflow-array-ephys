import json
import numpy as np
import pandas as pd
from pytest import mark


__all__ = [
    "dj_config",
    "pipeline",
    "test_data",
    "subjects_csv",
    "ingest_subjects",
    "sessions_csv",
    "ingest_sessions",
    "testdata_paths",
    "kilosort_paramset",
    "ephys_recordings",
    "clustering_tasks",
    "clustering",
    "curations",
]

from . import (
    dj_config,
    pipeline,
    test_data,
    subjects_csv,
    ingest_subjects,
    sessions_csv,
    ingest_sessions,
    testdata_paths,
    kilosort_paramset,
    ephys_recordings,
    clustering_tasks,
    clustering,
    curations,
)


def test_ephys_recording_populate(pipeline, ephys_recordings):
    ephys = pipeline["ephys"]
    assert len(ephys.EphysRecording()) == 13


def test_LFP_populate_npx3B_OpenEphys(testdata_paths, pipeline, ephys_recordings):
    """
    Populate ephys.LFP with OpenEphys items,
    recording Neuropixels Phase 3B (Neuropixels 1.0) probe
    """
    ephys = pipeline["ephys"]
    rel_path = testdata_paths["oe_npx3B"]
    rec_key = (
        ephys.EphysRecording
        & (ephys.EphysRecording.EphysFile & f'file_path LIKE "%{rel_path}"')
    ).fetch1("KEY")
    ephys.LFP.populate(rec_key)

    lfp_mean = (ephys.LFP & rec_key).fetch1("lfp_mean")
    assert len(lfp_mean) == 520054

    electrodes = (ephys.LFP.Electrode & rec_key).fetch("electrode")
    assert np.array_equal(
        electrodes,
        np.array(
            [
                5,
                14,
                23,
                32,
                41,
                50,
                59,
                68,
                77,
                86,
                95,
                104,
                113,
                122,
                131,
                140,
                149,
                158,
                167,
                176,
                185,
                194,
                203,
                212,
                221,
                230,
                239,
                248,
                257,
                266,
                275,
                284,
                293,
                302,
                311,
                320,
                329,
                338,
                347,
                356,
                365,
                374,
                383,
            ]
        ),
    )


def test_LFP_populate_npx3A_SpikeGLX(testdata_paths, pipeline, ephys_recordings):
    """Populate ephys.LFP with SpikeGLX items, recording Neuropixels Phase 3A probe"""
    ephys = pipeline["ephys"]

    rel_path = testdata_paths["sglx_npx3A-p1"]
    rec_key = (
        ephys.EphysRecording
        & (ephys.EphysRecording.EphysFile & f'file_path LIKE "%{rel_path}%"')
    ).fetch1("KEY")
    ephys.LFP.populate(rec_key)

    lfp_mean = (ephys.LFP & rec_key).fetch1("lfp_mean")
    assert len(lfp_mean) == 846666

    electrodes = (ephys.LFP.Electrode & rec_key).fetch("electrode")
    assert np.array_equal(
        electrodes,
        np.array(
            [
                5,
                14,
                23,
                32,
                41,
                50,
                59,
                68,
                77,
                86,
                95,
                104,
                113,
                122,
                131,
                140,
                149,
                158,
                167,
                176,
                185,
                194,
                203,
                212,
                221,
                230,
                239,
                248,
                257,
                266,
                275,
                284,
                293,
                302,
                311,
                320,
                329,
                338,
                347,
                356,
                365,
                374,
                383,
            ]
        ),
    )


def test_LFP_populate_npx3B_SpikeGLX(testdata_paths, pipeline, ephys_recordings):
    """
    Populate ephys.LFP with SpikeGLX items,
    recording Neuropixels Phase 3B (Neuropixels 1.0) probe
    """

    ephys = pipeline["ephys"]

    rel_path = testdata_paths["sglx_npx3B-p1"]
    rec_key = (
        ephys.EphysRecording
        & (ephys.EphysRecording.EphysFile & f'file_path LIKE "%{rel_path}%"')
    ).fetch1("KEY")
    ephys.LFP.populate(rec_key)

    lfp_mean = (ephys.LFP & rec_key).fetch1("lfp_mean")
    assert len(lfp_mean) == 4769946

    electrodes = (ephys.LFP.Electrode & rec_key).fetch("electrode")
    assert np.array_equal(
        electrodes,
        np.array(
            [
                5,
                14,
                23,
                32,
                41,
                50,
                59,
                68,
                77,
                86,
                95,
                104,
                113,
                122,
                131,
                140,
                149,
                158,
                167,
                176,
                185,
                194,
                203,
                212,
                221,
                230,
                239,
                248,
                257,
                266,
                275,
                284,
                293,
                302,
                311,
                320,
                329,
                338,
                347,
                356,
                365,
                374,
                383,
            ]
        ),
    )


def test_clustering_populate(clustering, pipeline):
    ephys = pipeline["ephys"]
    assert len(ephys.Clustering()) == 13


def test_curated_clustering_populate(curations, pipeline, testdata_paths):
    """Populate ephys.CuratedClustering with multiple recordings"""
    ephys = pipeline["ephys"]

    rel_path = testdata_paths["npx3A-p1-ks"]
    curation_key = _get_curation_key(rel_path, pipeline)
    ephys.CuratedClustering.populate(curation_key)
    assert (
        len(
            ephys.CuratedClustering.Unit
            & curation_key
            & 'cluster_quality_label = "good"'
        )
        == 76
    )

    rel_path = testdata_paths["oe_npx3B-ks"]
    curation_key = _get_curation_key(rel_path, pipeline)
    ephys.CuratedClustering.populate(curation_key)
    assert (
        len(
            ephys.CuratedClustering.Unit
            & curation_key
            & 'cluster_quality_label = "good"'
        )
        == 68
    )

    rel_path = testdata_paths["npx3B-p1-ks"]
    curation_key = _get_curation_key(rel_path, pipeline)
    ephys.CuratedClustering.populate(curation_key)
    assert (
        len(
            ephys.CuratedClustering.Unit
            & curation_key
            & 'cluster_quality_label = "good"'
        )
        == 55
    )


def test_waveform_populate_npx3B_OpenEphys(curations, pipeline, testdata_paths):
    """
    Populate ephys.WaveformSet with OpenEphys
    Neuropixels Phase 3B (Neuropixels 1.0) probe
    """
    ephys = pipeline["ephys"]
    rel_path = testdata_paths["oe_npx3B-ks"]
    curation_key = _get_curation_key(rel_path, pipeline)
    ephys.CuratedClustering.populate(curation_key)
    ephys.WaveformSet.populate(curation_key)

    waveforms = np.vstack(
        (ephys.WaveformSet.PeakWaveform & curation_key).fetch("peak_electrode_waveform")
    )

    assert waveforms.shape == (204, 64)


def test_waveform_populate_npx3B_SpikeGLX(curations, pipeline, testdata_paths):
    """
    Populate ephys.WaveformSet with SpikeGLX
    Neuropixels Phase 3B (Neuropixels 1.0) probe
    """

    ephys = pipeline["ephys"]

    rel_path = testdata_paths["npx3B-p1-ks"]
    curation_key = _get_curation_key(rel_path, pipeline)
    ephys.CuratedClustering.populate(curation_key)
    ephys.WaveformSet.populate(curation_key)

    waveforms = np.vstack(
        (ephys.WaveformSet.PeakWaveform & curation_key).fetch("peak_electrode_waveform")
    )

    assert waveforms.shape == (150, 64)


def test_build_electrode_layouts(pipeline):
    """
    Test build_electrode_layouts function in probe.py
    """

    # Load probe configuration
    f = open("user_data/neuropixels_probes_config.json")
    probe_configs = json.load(f)
    # Load ground truth table for each probe type
    truth_df = pd.read_csv("user_data/probe_type_electrode.csv")

    probe = pipeline["probe"]

    for probe_type, config in probe_configs.items():

        test_df = pd.DataFrame(probe.build_electrode_layouts(probe_type, **config))

        test_arr = np.array(test_df.drop(columns=["probe_type"]), dtype=np.int16)
        truth_arr = np.array(
            truth_df.loc[truth_df["probe_type"] == probe_type].drop(
                columns=["probe_type"]
            ),
            dtype=np.int16,
        )
        assert np.array_equal(
            test_arr, truth_arr
        ), f"probe type '{probe_type}' electrode layout does not match"


# ---- HELPER FUNCTIONS ----


def _get_curation_key(output_relative_path, pipeline):
    ephys = pipeline["ephys"]
    ephys_mode = pipeline["ephys_mode"]

    if ephys_mode == "no-curation":
        EphysCuration = ephys.ClusteringTask
        output_dir_attr_name = "clustering_output_dir"
    else:
        EphysCuration = ephys.Curation
        output_dir_attr_name = "curation_output_dir"

    return (
        EphysCuration & f'{output_dir_attr_name} LIKE "%{output_relative_path}"'
    ).fetch1("KEY")
