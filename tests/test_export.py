import sys
import pathlib
import numpy as np

from . import (dj_config, pipeline, test_data,
               subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, kilosort_paramset,
               ephys_recordings, clustering_tasks, clustering, curations)


def test_subject_nwb_export(ingest_subjects, pipeline):
    subject = pipeline['subject']
    subject_key = {'subject': 'subject1'}
    nwb_subject = subject.Subject.make_nwb(subject_key)

    subject_info = (subject.Subject & subject_key).fetch1()

    assert nwb_subject.subject_id == subject_info['subject']
    assert nwb_subject.sex == subject_info['sex']
    assert nwb_subject.date_of_birth.date() == subject_info['subject_birth_date']


def test_session_nwb_export(ingest_sessions, pipeline):
    session = pipeline['session']
    session_key = {'subject': 'subject1', 'session_datetime': '2018-11-22 18:51:26'}
    nwb_session = session.Session.make_nwb(session_key)

    session_info = (session.Session & session_key).fetch1()

    assert nwb_session.session_start_time.strftime('%Y%m%d_%H%M%S') == session_info['session_datetime'].strftime('%Y%m%d_%H%M%S')
    assert nwb_session.subject.subject_id == session_info['subject']
    assert nwb_session.experimenter == list(session.SessionExperimenter.fetch('user'))


def test_ephys_nwb_export(curations, pipeline, testdata_paths):
    ephys = pipeline['ephys']
    probe = pipeline['probe']

    rel_path = testdata_paths['npx3B-p1-ks']
    curation_key = (ephys.Curation & f'curation_output_dir LIKE "%{rel_path}"').fetch1('KEY')
    ephys.CuratedClustering.populate(curation_key)
    ephys.LFP.populate(curation_key)
    ephys.WaveformSet.populate(curation_key)

    nwb_ephys = ephys.CuratedClustering.make_nwb(curation_key)

    probe_name, probe_type = (ephys.ProbeInsertion * probe.Probe * probe.ProbeType
                              & curation_key).fetch1('probe', 'probe_type')

    device_name = f'{probe_name} ({probe_type})'
    assert device_name in nwb_ephys.devices

    # check LFP
    lfp_name = f'probe_{probe_name} - LFP'
    assert lfp_name in nwb_ephys.processing['ecephys'].data_interfaces

    lfp_timestamps = (ephys.LFP & curation_key).fetch1('lfp_time_stamps')
    lfp_channel_count = len((ephys.LFP.Electrode & curation_key))

    nwb_lfp = nwb_ephys.processing['ecephys'].data_interfaces[lfp_name].electrical_series['processed_electrical_series']
    assert nwb_lfp.data.shape == (len(lfp_timestamps), lfp_channel_count)

    # check electrodes
    nwb_electrodes = nwb_ephys.electrodes.to_dataframe()
    electrodes = (ephys.EphysRecording * probe.ElectrodeConfig.Electrode
                  * probe.ProbeType.Electrode & curation_key).fetch(
        format='frame').reset_index()
    assert np.array_equal(nwb_electrodes.index, electrodes.index)
    assert np.array_equal(nwb_electrodes.rel_x, electrodes.x_coord)
    assert np.array_equal(nwb_electrodes.rel_y, electrodes.y_coord)

    # check Unit
    nwb_units = nwb_ephys.units.to_dataframe()

    assert len(ephys.CuratedClustering.Unit & curation_key) == len(nwb_units)
    assert len(ephys.CuratedClustering.Unit & curation_key & 'cluster_quality_label = "good"') == sum(nwb_units.cluster_quality_label == 'good')

    # check waveform

    assert np.array_equal(
        nwb_units.iloc[15].waveform_mean,
        (ephys.WaveformSet.PeakWaveform & curation_key
         & 'unit = 15').fetch1('peak_electrode_waveform')
    )
