import csv
import re

from workflow_array_ephys.pipeline import subject, ephys, probe, session, trial, event
from workflow_array_ephys.paths import get_ephys_root_data_dir
from workflow_array_ephys.pipeline import ephys_mode

from element_array_ephys.readers import spikeglx, openephys
from element_interface.utils import find_root_directory, find_full_path


def ingest_general(csvs, tables, skip_duplicates=True, verbose=True,
                   allow_direct_insert=False):
    """
    Inserts data from a series of csvs into their corresponding table:
        e.g., ingest_general(['./lab_data.csv', './proj_data.csv'],
                                 [lab.Lab(),lab.Project()]
    ingest_general(csvs, tables, skip_duplicates=True, verbose=True,
                   allow_direct_insert=False)
        :param csvs: list of relative paths to CSV files.  CSV are delimited by commas.
        :param tables: list of datajoint tables with ()
        :param verbose: print number inserted (i.e., table length change)
        :param skip_duplicates: skip items that are either (a) duplicates within the csv
                                or (b) already exist in the corresponding table
        :param allow_direct_insert: Permit insertion directly into calculated tables
    """
    for csv_filepath, table in zip(csvs, tables):
        with open(csv_filepath, newline='') as f:
            data = list(csv.DictReader(f, delimiter=','))
        if verbose:
            prev_len = len(table)
        table.insert(data, skip_duplicates=skip_duplicates,
                     # Ignore extra fields because some CSVs feed multiple tables
                     ignore_extra_fields=True, allow_direct_insert=allow_direct_insert)
        if verbose:
            insert_len = len(table) - prev_len     # report length change
            print(f'\n---- Inserting {insert_len} entry(s) '
                  + f'into {table.table_name} ----')


def ingest_subjects(subject_csv_path='./user_data/subjects.csv',
                    skip_duplicates=True, verbose=True):
    """
    Ingest subjects listed in the subject column of ./user_data/subjects.csv
    """
    csvs = [subject_csv_path]
    tables = [subject.Subject()]

    ingest_general(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


def ingest_sessions(session_csv_path='./user_data/sessions.csv', verbose=True,
                    skip_duplicates=False):
    """
    Ingests SpikeGLX and OpenEphys files from directories listed
    in the session_dir column of ./user_data/sessions.csv
    """
    # ---------- Insert new "Session" and "ProbeInsertion" ---------
    with open(session_csv_path, newline='') as f:
        input_sessions = list(csv.DictReader(f, delimiter=','))

    # Folder structure: root / subject / session / probe / .ap.meta
    session_list, session_dir_list = [], []
    probe_list, probe_insertion_list = [], []

    for sess in input_sessions:
        session_dir = find_full_path(get_ephys_root_data_dir(),
                                     sess['session_dir'])
        session_datetimes, insertions = [], []

        # search session dir and determine acquisition software
        for ephys_pattern, ephys_acq_type in zip(['*.ap.meta', '*.oebin'],
                                                 ['SpikeGLX', 'OpenEphys']):
            ephys_meta_filepaths = [fp for fp in session_dir.rglob(ephys_pattern)]
            if len(ephys_meta_filepaths):
                acq_software = ephys_acq_type
                break
        else:
            raise FileNotFoundError('Ephys recording data not found! Neither SpikeGLX '
                                    + 'nor OpenEphys recording files found in: '
                                    + f'{session_dir}')

        if acq_software == 'SpikeGLX':
            for meta_filepath in ephys_meta_filepaths:
                spikeglx_meta = spikeglx.SpikeGLXMeta(meta_filepath)

                probe_key = {'probe_type': spikeglx_meta.probe_model,
                             'probe': spikeglx_meta.probe_SN}
                if (probe_key['probe'] not in [p['probe'] for p in probe_list
                                               ] and probe_key not in probe.Probe()):
                    probe_list.append(probe_key)

                probe_dir = meta_filepath.parent
                probe_number = re.search('(imec)?\d{1}$', probe_dir.name
                                         ).group()
                probe_number = int(probe_number.replace('imec', ''))

                insertions.append({'probe': spikeglx_meta.probe_SN,
                                   'insertion_number': int(probe_number)})
                session_datetimes.append(spikeglx_meta.recording_time)
        elif acq_software == 'OpenEphys':
            loaded_oe = openephys.OpenEphys(session_dir)
            session_datetimes.append(loaded_oe.experiment.datetime)
            for probe_idx, oe_probe in enumerate(loaded_oe.probes.values()):
                probe_key = {'probe_type': oe_probe.probe_model,
                             'probe': oe_probe.probe_SN}
                if (probe_key['probe'] not in [p['probe'] for p in probe_list
                                               ] and probe_key not in probe.Probe()):
                    probe_list.append(probe_key)
                insertions.append({'probe': oe_probe.probe_SN,
                                   'insertion_number': probe_idx})
        else:
            raise NotImplementedError('Unknown acquisition software: '
                                      + f'{acq_software}')

        # new session/probe-insertion
        session_key = {'subject': sess['subject'],
                       'session_datetime': min(session_datetimes)}
        if session_key not in session.Session():
            session_list.append(session_key)
            root_dir = find_root_directory(get_ephys_root_data_dir(), session_dir)
            session_dir_list.append({**session_key, 'session_dir':
                                     session_dir.relative_to(root_dir).as_posix()})
            probe_insertion_list.extend([{**session_key, **insertion
                                          } for insertion in insertions])

    session.Session.insert(session_list)
    session.SessionDirectory.insert(session_dir_list)
    if verbose:
        print(f'\n---- Insert {len(session_list)} entry(s) into session.Session ----')

    probe.Probe.insert(probe_list)
    if verbose:
        print(f'\n---- Insert {len(probe_list)} entry(s) into probe.Probe ----')

    if ephys_mode == 'chronic':
        ephys.ProbeInsertion.insert(probe_insertion_list,
                                    ignore_extra_fields=True, skip_duplicates=True)
        session.Session.insert(session_list)
        session.SessionDirectory.insert(session_dir_list)
        if verbose:
            print(f'\n---- Insert {len(probe_insertion_list)} entry(s) into '
                  + 'ephys.ProbeInsertion ----')
            print(f'\n---- Insert {len(session_list)} entry(s) into '
                  + 'session.Session ----')
    else:
        session.Session.insert(session_list)
        session.SessionDirectory.insert(session_dir_list)
        ephys.ProbeInsertion.insert(probe_insertion_list)
        if verbose:
            print(f'\n---- Insert {len(probe_insertion_list)} entry(s) into '
                  + 'ephys.ProbeInsertion ----')
            print(f'\n---- Insert {len(session_list)} entry(s) into '
                  + 'session.Session ----')

    print('\n---- Successfully completed workflow_array_ephys/ingest.py ----')


def ingest_events(recording_csv_path='./user_data/behavior_recordings.csv',
                  block_csv_path='./user_data/blocks.csv',
                  trial_csv_path='./user_data/trials.csv',
                  event_csv_path='./user_data/events.csv',
                  skip_duplicates=True, verbose=True):
    csvs = [recording_csv_path, recording_csv_path,
            block_csv_path, block_csv_path,
            trial_csv_path, trial_csv_path, trial_csv_path,
            trial_csv_path,
            event_csv_path, event_csv_path, event_csv_path]
    tables = [event.BehaviorRecording(), event.BehaviorRecording.File(),
              trial.Block(), trial.Block.Attribute(),
              trial.TrialType(), trial.Trial(), trial.Trial.Attribute(),
              trial.BlockTrial(),
              event.EventType(), event.Event(), trial.TrialEvent()]

    # Allow direct insert required bc element-trial has Imported that should be Manual
    ingest_general(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose,
                   allow_direct_insert=True)


def ingest_alignment(alignment_csv_path='./user_data/alignments.csv',
                     skip_duplicates=True, verbose=True):

    csvs = [alignment_csv_path]
    tables = [event.AlignmentEvent()]

    ingest_general(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


if __name__ == '__main__':
    ingest_subjects()
    ingest_sessions()
    ingest_events()
    ingest_alignment()
