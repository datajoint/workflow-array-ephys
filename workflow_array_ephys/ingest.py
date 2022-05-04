import csv
import re

from workflow_array_ephys.pipeline import lab, subject, ephys, probe, session, trial, \
                                          event
from workflow_array_ephys.paths import get_ephys_root_data_dir

from element_array_ephys.readers import spikeglx, openephys
from element_interface.utils import find_root_directory, find_full_path, \
                                    ingest_csv_to_table


def ingest_lab(lab_csv_path='./user_data/lab/labs.csv',
               project_csv_path='./user_data/lab/projects.csv',
               publication_csv_path='./user_data/lab/publications.csv',
               keyword_csv_path='./user_data/lab/keywords.csv',
               protocol_csv_path='./user_data/lab/protocols.csv',
               users_csv_path='./user_data/lab/users.csv',
               project_user_csv_path='./user_data/lab/project_users.csv',
               skip_duplicates=True, verbose=True):
    """
    Inserts data from a CSVs into their corresponding lab schema tables.
    By default, uses data from workflow_session/user_data/lab/
    :param lab_csv_path:      relative path of lab csv
    :param project_csv_path:  relative path of project csv
    :param publication_csv_path:     relative path of publication csv
    :param keyword_csv_path:     relative path of keyword csv
    :param protocol_csv_path: relative path of protocol csv
    :param users_csv_path:    relative path of users csv
    :param project_user_csv_path: relative path of project users csv
    :param skip_duplicates=True: datajoint insert function param
    :param verbose: print number inserted (i.e., table length change)
    """

    # List with repeats for when mult dj.tables fed by same CSV
    csvs = [lab_csv_path, lab_csv_path,
            project_csv_path, project_csv_path,
            publication_csv_path, keyword_csv_path,
            protocol_csv_path, protocol_csv_path,
            users_csv_path, users_csv_path, users_csv_path,
            project_user_csv_path]
    tables = [lab.Lab(), lab.Location(),
              lab.Project(), lab.ProjectSourceCode(),
              lab.ProjectPublication(), lab.ProjectKeywords(),
              lab.ProtocolType(), lab.Protocol(),
              lab.UserRole(), lab.User(), lab.LabMembership(),
              lab.ProjectUser()]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


def ingest_subjects(subject_csv_path='./user_data/subjects.csv', verbose=True):
    """
    Ingest subjects listed in the subject column of ./user_data/subjects.csv
    """
    # -------------- Insert new "Subject" --------------
    with open(subject_csv_path, newline='') as f:
        input_subjects = list(csv.DictReader(f, delimiter=','))
    if verbose:
        previous_length = len(subject.Subject.fetch())
    subject.Subject.insert(input_subjects, skip_duplicates=True)
    if verbose:
        insert_length = len(subject.Subject.fetch()) - previous_length
        print(f'\n---- Insert {insert_length} entry(s) into '
              + 'subject.Subject ----')
        print('\n---- Successfully completed ingest_subjects ----')


def ingest_sessions(session_csv_path='./user_data/sessions.csv', verbose=True):
    """
    Ingests SpikeGLX and OpenEphys files from directories listed
    in the session_dir column of ./user_data/sessions.csv
    """
    # ---------- Insert new "Session" and "ProbeInsertion" ---------
    with open(session_csv_path, newline='') as f:
        input_sessions = list(csv.DictReader(f, delimiter=','))

    # Folder structure: root / subject / session / probe / .ap.meta
    session_list, session_dir_list, = [], []
    session_note_list, session_experimenter_list = [], []
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
            session_note_list.append({**session_key, 'session_note':
                                      sess['session_note']})
            session_experimenter_list.append({**session_key, 'user':
                                              sess['user']})
            probe_insertion_list.extend([{**session_key, **insertion
                                          } for insertion in insertions])

    session.Session.insert(session_list)
    session.SessionDirectory.insert(session_dir_list)
    session.SessionNote.insert(session_note_list)
    session.SessionExperimenter.insert(session_experimenter_list)
    if verbose:
        print(f'\n---- Insert {len(session_list)} entry(s) into session.Session ----')

    probe.Probe.insert(probe_list)
    if verbose:
        print(f'\n---- Insert {len(probe_list)} entry(s) into probe.Probe ----')

    ephys.ProbeInsertion.insert(probe_insertion_list)
    if verbose:
        print(f'\n---- Insert {len(probe_insertion_list)} entry(s) into '
              + 'ephys.ProbeInsertion ----')
        print('\n---- Successfully completed ingest_subjects ----')


def ingest_events(recording_csv_path='./user_data/behavior_recordings.csv',
                  block_csv_path='./user_data/blocks.csv',
                  trial_csv_path='./user_data/trials.csv',
                  event_csv_path='./user_data/events.csv',
                  skip_duplicates=True, verbose=True):
    """
    Ingest each level of experiment heirarchy for element-trial:
        recording, block (i.e., phases of trials), trials (repeated units),
        events (optionally 0-duration occurances within trial).
    This ingestion function is duplicated across wf-array-ephys and wf-calcium-imaging
    """
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
    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose,
                        allow_direct_insert=True)


def ingest_alignment(alignment_csv_path='./user_data/alignments.csv',
                     skip_duplicates=True, verbose=True):
    """This is duplicated across wf-array-ephys and wf-calcium-imaging"""

    csvs = [alignment_csv_path]
    tables = [event.AlignmentEvent()]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


if __name__ == '__main__':
    ingest_subjects()
    ingest_sessions()
    ingest_events()
    ingest_alignment()
