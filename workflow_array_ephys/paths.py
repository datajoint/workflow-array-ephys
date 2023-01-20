import pathlib

import datajoint as dj
from element_interface.utils import find_full_path


def get_ephys_root_data_dir():
    """Return root directory for ephys from 'ephys_root_data_dir' in dj.config

    Returns:
        path (any): List of path(s) if available or None
    """
    return dj.config.get("custom", {}).get("ephys_root_data_dir", None)


def get_session_directory(session_key: dict) -> str:
    """Return relative path from SessionDirectory table given key

    Args:
        session_key (dict): Key uniquely identifying a session

    Returns:
        path (str): Relative path of session directory
    """
    from .pipeline import session

    session_dir = (session.SessionDirectory & session_key).fetch1("session_dir")
    return session_dir


def get_electrode_localization_dir(probe_insertion_key: dict) -> str:
    """Return root directory of localization data for a given probe

    Args:
        probe_insertion_key (dict): key uniquely identifying one ephys.EphysRecording

    Returns:
        path (str): Full path to localization data for either SpikeGLX or OpenEphys
    """
    from .pipeline import ephys

    acq_software = (ephys.EphysRecording & probe_insertion_key).fetch1("acq_software")

    if acq_software == "SpikeGLX":
        spikeglx_meta_filepath = pathlib.Path(
            (
                ephys.EphysRecording.EphysFile
                & probe_insertion_key
                & 'file_path LIKE "%.ap.meta"'
            ).fetch1("file_path")
        )
        probe_dir = find_full_path(
            get_ephys_root_data_dir(), spikeglx_meta_filepath.parent
        )
    elif acq_software == "Open Ephys":
        probe_path = (ephys.EphysRecording.EphysFile & probe_insertion_key).fetch1(
            "file_path"
        )
        probe_dir = find_full_path(get_ephys_root_data_dir(), probe_path)

    return probe_dir
