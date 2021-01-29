import re
import pathlib
import csv

from .pipeline import subject, ephys, probe, Session
from .paths import get_ephys_root_data_dir

from elements_ephys.readers import neuropixels


def ingest_subjects():
    # -------------- Insert new "Subject" --------------
    with open('./user_data/subjects.csv', newline='') as f:
        subjects_dict = list(csv.DictReader(f, delimiter=','))

    print(f'\n---- Insert {len(subjects_dict)} entry(s) into subject.Subject ----')
    subject.Subject.insert(subjects_dict, skip_duplicates=True)


def ingest_sessions():
    root_data_dir = get_ephys_root_data_dir()

    # ---------- Insert new "Session" and "ProbeInsertion" ---------
    with open('./user_data/sessions.csv', newline='') as f:
        sessions_dict = list(csv.DictReader(f, delimiter=','))

    # Folder structure: root / subject / session / probe / .ap.meta
    session_list, session_dir_list, probe_insertion_list, probe_list = [], [], [], []

    for sess in sessions_dict:
        sess_dir = pathlib.Path(sess['session_dir'])
        session_datetimes, insertions = [], []

        meta_filepaths = list(sess_dir.rglob('*.ap.meta'))

        if len(meta_filepaths) == 0:
            print(f'Session data not found! No ".ap.meta" files found in {sess_dir}. Skipping...')
            continue

        for meta_filepath in meta_filepaths:
            npx_meta = neuropixels.NeuropixelsMeta(meta_filepath)

            prb = {'probe_type': npx_meta.probe_model, 'probe': npx_meta.probe_SN}
            if prb not in probe.Probe.proj() and prb['probe'] not in [p['probe'] for p in probe_list]:
                probe_list.append(prb)

            probe_dir = meta_filepath.parent
            probe_number = re.search('(imec)?\d{1}$', probe_dir.name).group()
            probe_number = int(probe_number.replace('imec', '')) if 'imec' in probe_number else int(probe_number)

            insertions.append({'probe': npx_meta.probe_SN, 'insertion_number': int(probe_number)})
            session_datetimes.append(npx_meta.recording_time)

        session_key = {'subject': sess['subject'], 'session_datetime': min(session_datetimes)}
        if session_key not in Session.proj():
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
