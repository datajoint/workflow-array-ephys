import re
import pathlib
import csv

import datajoint as dj 
dj.conn()

from workflow_array_ephys.pipeline import subject, ephys, probe, session
from workflow_array_ephys.paths import get_ephys_root_data_dir

from element_array_ephys.readers import spikeglx, openephys
import element_data_loader.utils

session_csv_path='../user_data/sessions.csv'
root_data_dir = get_ephys_root_data_dir()

# ---------- Insert new "Session" and "ProbeInsertion" ---------
with open(session_csv_path, newline= '') as f:
    input_sessions = list(csv.DictReader(f, delimiter=','))

# Folder structure: root / subject / session / probe / .ap.meta
session_list, session_dir_list, probe_list, probe_insertion_list = [], [], [], []

for sess in input_sessions:
    session_dir = element_data_loader.utils.find_full_path(
                                                get_ephys_root_data_dir(), 
                                                sess['session_dir'])
    session_datetimes, insertions = [], []

    # search session dir and determine acquisition software
    for ephys_pattern, ephys_acq_type in zip(['*.ap.meta', '*.oebin'], ['SpikeGLX', 'OpenEphys']):
        ephys_meta_filepaths = [fp for fp in session_dir.rglob(ephys_pattern)]
        if len(ephys_meta_filepaths):
            acq_software = ephys_acq_type
            break
    else:
        raise FileNotFoundError(f'Ephys recording data not found! Neither SpikeGLX nor OpenEphys recording files found in: {session_dir}')

    # new session/probe-insertion
    session_key = {'subject': sess['subject'], 'session_datetime': min('1999-01-01')}

    # print('session_key')
    # print(session_key)
    # print('session_dir')
    # print(session_dir)#.relative_to(root_data_dir).as_posix())

    import pdb; pdb.set_trace()  # breakpoint 7aa166a4 //
    if session_key not in session.Session():
        session_list.append(session_key)
        session_dir_list.append({**session_key, 'session_dir': session_dir.relative_to(root_data_dir).as_posix()})
        probe_insertion_list.extend([{**session_key, **insertion} for insertion in insertions])

print(f'\n---- Insert {len(session_list)} entry(s) into session.Session ----')
session.Session.insert(session_list)
session.SessionDirectory.insert(session_dir_list)

print(f'\n---- Insert {len(probe_list)} entry(s) into probe.Probe ----')
probe.Probe.insert(probe_list)

print(f'\n---- Insert {len(probe_insertion_list)} entry(s) into ephys.ProbeInsertion ----')
ephys.ProbeInsertion.insert(probe_insertion_list)

print('\n---- Successfully completed workflow_array_ephys/ingest.py ----')