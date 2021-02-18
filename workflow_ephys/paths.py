import datajoint as dj
import pathlib


def get_ephys_root_data_dir():
    data_dir = dj.config.get('custom', {}).get('ephys_root_data_dir', None)
    return pathlib.Path(data_dir) if data_dir else None


def get_session_directory(session_key: dict) -> str:
    # Folder structure: root / subject / session
    data_dir = get_ephys_root_data_dir()

    from .pipeline import Session
    sess_dir = data_dir / (Session.Directory & session_key).fetch1('session_dir')

    return sess_dir.as_posix()


def get_ephys_probe_data_dir(probe_key):
    # Folder structure: root / subject / session / probe / .ap.meta
    data_dir = get_ephys_root_data_dir()

    from .pipeline import Session
    sess_dir = data_dir / (Session.Directory & probe_key).fetch1('session_dir')

    if not sess_dir.exists():
        raise FileNotFoundError(f'Session directory not found ({sess_dir})')

    probe_no = probe_key['insertion_number']

    probe_dir_pattern = f'*{probe_no}'
    npx_meta_pattern = f'*{probe_no}.ap.meta'

    search_pattern = '/'.join([probe_dir_pattern, npx_meta_pattern])

    try:
        npx_meta_fp = next(sess_dir.rglob(search_pattern))
    except StopIteration:
        raise FileNotFoundError(f'Unable to find probe directory matching: {search_pattern} (in {sess_dir})')

    return npx_meta_fp.parent


ks2specs = ('mean_waveforms.npy', 'spike_times.npy')  # prioritize QC output, then orig


def get_ks_data_dir(probe_key):
    probe_dir = get_ephys_probe_data_dir(probe_key)

    ks2spec = ks2specs[0] if len(list(probe_dir.rglob(ks2specs[0]))) > 0 else ks2specs[1]
    ks2files = [f.parent for f in probe_dir.rglob(ks2spec)]

    if len(ks2files) > 1:
        raise ValueError('Multiple Kilosort outputs found at: {}'.format([x.as_poxis() for x in ks2files]))

    return ks2files[0]


def get_paramset_idx(rec_key):
    return 0
