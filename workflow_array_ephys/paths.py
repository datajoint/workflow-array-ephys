import datajoint as dj
import pathlib


def get_ephys_root_data_dir():
    root_data_dirs = dj.config.get('custom', {}).get('ephys_root_data_dir', None)
    return root_data_dirs if root_data_dirs else None

def get_session_directory(session_key: dict) -> str:
    from .pipeline import session
    session_dir = (session.SessionDirectory & session_key).fetch1('session_dir')
    return session_dir