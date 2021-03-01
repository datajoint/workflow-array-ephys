import re
import pathlib
import csv

from workflow_ephys.pipeline import subject, ephys, probe, Session
from workflow_ephys.paths import get_ephys_root_data_dir

from elements_ephys.readers import spikeglx, openephys


def ingest_subjects():
    # -------------- Insert new "Subject" --------------
    with open('./user_data/subjects.csv', newline='') as f:
        input_subjects = list(csv.DictReader(f, delimiter=','))

    print(f'\n---- Insert {len(input_subjects)} entry(s) into subject.Subject ----')
    subject.Subject.insert(input_subjects, skip_duplicates=True)


def ingest_sessions():
    root_data_dir = get_ephys_root_data_dir()

    # ---------- Insert new "Session" and "ProbeInsertion" ---------
    with open('./user_data/sessions.csv', newline='') as f:
        input_sessions = list(csv.DictReader(f, delimiter=','))

    # Folder structure: root / subject / session / probe / .ap.meta
    session_list, session_dir_list, probe_list, probe_insertion_list = [], [], [], []

    for sess in input_sessions:
        sess_dir = pathlib.Path(sess['session_dir'])
        session_datetimes, insertions = [], []

        # search session dir and determine acquisition software
        acq_software = None
        for ephys_pattern, ephys_acq_type in zip(['*.ap.meta', '*.oebin'], ['SpikeGLX', 'OpenEphys']):
            ephys_meta_filepaths = [fp for fp in sess_dir.rglob(ephys_pattern)]
            if len(ephys_meta_filepaths):
                acq_software = ephys_acq_type
                break

        if acq_software is None:
            raise FileNotFoundError(f'Ephys recording data not found! Neither SpikeGLX nor OpenEphys recording files found in: {sess_dir}')

        if acq_software == 'SpikeGLX':
            for meta_filepath in ephys_meta_filepaths:
                spikeglx_meta = spikeglx.SpikeGLXMeta(meta_filepath)

                probe_key = {'probe_type': spikeglx_meta.probe_model, 'probe': spikeglx_meta.probe_SN}
                if probe_key not in probe.Probe.proj() and probe_key['probe'] not in [p['probe'] for p in probe_list]:
                    probe_list.append(probe_key)

                probe_dir = meta_filepath.parent
                probe_number = re.search('(imec)?\d{1}$', probe_dir.name).group()
                probe_number = int(probe_number.replace('imec', ''))

                insertions.append({'probe': spikeglx_meta.probe_SN, 'insertion_number': int(probe_number)})
                session_datetimes.append(spikeglx_meta.recording_time)

        elif acq_software == 'OpenEphys':
            loaded_oe = openephys.OpenEphys(sess_dir)
            session_datetimes.append(loaded_oe.experiment.datetime)
            for probe_idx, oe_probe in enumerate(loaded_oe.probes):
                probe_key = {'probe_type': oe_probe['probe_model'], 'probe': oe_probe['probe_SN']}
                if probe_key['probe'] not in [p['probe'] for p in probe_list] and probe_key not in probe.Probe():
                    probe_list.append(probe_key)
                insertions.append({'probe': oe_probe['probe_SN'], 'insertion_number': probe_idx})

        # new session/probe-insertion
        session_key = {'subject': sess['subject'], 'session_datetime': min(session_datetimes)}
        if session_key not in Session():
            session_list.append(session_key)
            session_dir_list.append({**session_key, 'session_dir': sess_dir.relative_to(root_data_dir).as_posix()})
            probe_insertion_list.extend([{**session_key, **insertion} for insertion in insertions])

    print(f'\n---- Insert {len(session_list)} entry(s) into experiment.Session ----')
    Session.insert(session_list)

    print(f'\n---- Insert {len(session_dir_list)} entry(s) into experiment.Session.Directory ----')
    Session.Directory.insert(session_dir_list)

    print(f'\n---- Insert {len(probe_list)} entry(s) into probe.Probe ----')
    probe.Probe.insert(probe_list)

    print(f'\n---- Insert {len(probe_insertion_list)} entry(s) into ephys.ProbeInsertion ----')
    ephys.ProbeInsertion.insert(probe_insertion_list)

    print('\n---- Successfully completed workflow_imaging/ingest.py ----')


if __name__ == '__main__':
    ingest_subjects()
    ingest_sessions()
