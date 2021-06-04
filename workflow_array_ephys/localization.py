import datajoint as dj
from element_electrode_localization import coordinate_framework, electrode_localization
from .pipeline import ephys, probe
from .paths import get_ephys_root_data_dir, get_session_directory, \
                   get_electrode_localization_dir


if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')

__all__ = ['ephys', 'probe', 'coordinate_framework', 'electrode_localization',
           'ProbeInsertion',
           'get_ephys_root_data_dir', 'get_session_directory',
           'get_electrode_localization_dir']

ProbeInsertion = ephys.ProbeInsertion
electrode_localization.activate(db_prefix + 'eloc',
                                db_prefix + 'ccf',
                                linking_module=__name__)

# Activate "electrode-localization" schema ------------------------------------

ProbeInsertion = ephys.ProbeInsertion
Electrode = probe.ProbeType.Electrode

electrode_localization.activate(db_prefix + 'electrode_localization',
                                db_prefix + 'ccf',
                                linking_module=__name__)
