import datajoint as dj
from element_electrode_localization import coordinate_framework, electrode_localization
from .pipeline import ephys, probe


if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')

__all__ = ['ephys', 'probe', 'coordinate_framework', 'electrode_localization',
           'ProbeInsertion']

ProbeInsertion = ephys.ProbeInsertion
electrode_localization.activate(db_prefix + 'eloc',
                                db_prefix + 'ccf',
                                linking_module=__name__)
