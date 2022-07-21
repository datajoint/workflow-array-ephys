# For didactic purposes, import upstream NWB export functions
from element_lab.export.nwb import element_lab_to_nwb_dict
from element_animal.export.nwb import subject_to_nwb
from element_session.export.nwb import session_to_nwb
from .pipeline import ephys_mode

__all__ = [
    "element_lab_to_nwb_dict",
    "subject_to_nwb",
    "session_to_nwb",
    "ecephys_session_to_nwb",
    "write_nwb",
]

# Import ephys NWB export functions
if ephys_mode == "no-curation":
    from element_array_ephys.export.nwb import ecephys_session_to_nwb, write_nwb
else:
    missing_ephys_warning = (
        f"Warning: ephys export requires the no-curation ephys_mode. To use it,\n\t"
        + "try setting datajoint.config['custom']['ephys_mode'] to 'no-curation'\n\t"
        + "and restarting your kernel."
    )

    def ecephys_session_to_nwb(*args):
        return missing_ephys_warning

    def write_nwb(*args):
        return missing_ephys_warning

    print(missing_ephys_warning)
