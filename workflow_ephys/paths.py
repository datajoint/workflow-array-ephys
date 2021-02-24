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
