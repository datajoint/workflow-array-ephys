import datajoint as dj
import pathlib


def get_ephys_root_data_dir():
    data_dir = dj.config.get('custom', {}).get('ephys_root_data_dir', None)
    return pathlib.Path(data_dir) if data_dir else None


def get_session_directory(session_key: dict) -> str:
    data_dir = get_ephys_root_data_dir()

    from .pipeline import session
    sess_dir = data_dir / (session.SessionDirectory & session_key).fetch1('session_dir')

    return sess_dir.as_posix()
