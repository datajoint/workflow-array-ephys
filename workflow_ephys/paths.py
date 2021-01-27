import datajoint as dj
import pathlib


def get_ephys_root_data_dir():
    data_dir = dj.config.get('custom', {}).get('ephys_root_data_dir', None)
    return pathlib.Path(data_dir) if data_dir else None


def get_ephys_probe_data_dir(probe_key):
    subj = probe_key['subject']
    probe_no = probe_key['insertion_number']
    sess_datetime_string = probe_key['session_datetime'].strftime('%m%d%y_%H%M%S')

    subj_dir = get_ephys_root_data_dir() / subj

    sess_dir_pattern = f'*{subj}_{sess_datetime_string}*'
    probe_dir_pattern = f'*imec{probe_no}'
    npx_meta_pattern = f'*imec{probe_no}.ap.meta'

    search_pattern = '/'.join([sess_dir_pattern, probe_dir_pattern, npx_meta_pattern])

    try:
        npx_meta_fp = next(subj_dir.rglob(search_pattern))
    except StopIteration:
        raise FileNotFoundError(f'Unable to find probe directory matching: {search_pattern}')

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
