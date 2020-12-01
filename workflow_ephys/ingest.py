import re

from elements_ephys.readers import neuropixels
from workflow_ephys.pipeline import subject, ephys, probe, Session
from workflow_ephys.utils.paths import get_ephys_root_data_dir


def ingest():
    # ========== Insert new "Session" ===========
    data_dir = get_ephys_root_data_dir()

    # Folder structure: root / subject / session / probe / .ap.meta
    sessions, sess_folder_names = [], []
    for subj_key in subject.Subject.fetch('KEY'):
        subj_dir = data_dir / subj_key['subject']
        if subj_dir.exists():
            for meta_filepath in subj_dir.rglob('*.ap.meta'):
                sess_folder = meta_filepath.parent.parent.name
                if sess_folder not in sess_folder_names:
                    npx_meta = neuropixels.NeuropixelsMeta(meta_filepath)
                    sessions.append({**subj_key, 'session_datetime': npx_meta.recording_time})
                    sess_folder_names.append(sess_folder)

    print(f'Inserting {len(sessions)} session(s)')
    Session.insert(sessions, skip_duplicates=True)

    # ========== Insert new "ProbeInsertion" ===========
    probe_insertions = []
    for sess_key in Session.fetch('KEY'):
        subj_dir = data_dir / sess_key['subject']
        if subj_dir.exists():
            for meta_filepath in subj_dir.rglob('*.ap.meta'):
                npx_meta = neuropixels.NeuropixelsMeta(meta_filepath)

                prb = {'probe_type': npx_meta.probe_model, 'probe': npx_meta.probe_SN}
                probe.Probe.insert1(prb, skip_duplicates=True)

                probe_dir = meta_filepath.parent
                probe_number = re.search('(imec)?\d{1}$', probe_dir.name).group()
                probe_number = int(probe_number.replace('imec', '')) if 'imec' in probe_number else int(probe_number)

                probe_insertions.append({**sess_key, **prb, 'insertion_number': int(probe_number)})

    print(f'Inserting {len(probe_insertions)} probe_insertion(s)')
    ephys.ProbeInsertion.insert(probe_insertions, ignore_extra_fields=True, skip_duplicates=True)


if __name__ == '__main__':
    ingest()
