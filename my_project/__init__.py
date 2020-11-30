import datajoint as dj
from djsubject import subject
from djlab import lab
from djephys import ephys
from utils.path_utils import get_ephys_probe_data_dir, get_ks_data_dir, get_paramset_idx

if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')


# ============== Declare "lab" and "subject" schema ==============

lab.declare(db_prefix + 'lab')

subject.declare(db_prefix + 'subject',
                dependencies={'Source': lab.Source,
                              'Lab': lab.Lab,
                              'Protocol': lab.Protocol,
                              'User': lab.User})


@lab.schema
class SkullReference(dj.Lookup):
    definition = """
    skull_reference   : varchar(60)
    """
    contents = zip(['Bregma', 'Lambda'])


# ============== Declare Session table ==============

schema = dj.schema(db_prefix + 'experiment')


@schema
class Session(dj.Manual):
    definition = """
    -> subject.Subject
    session_datetime: datetime
    """


# ============== Declare "ephys" schema ==============

ephys.declare(dj.schema(db_prefix + 'ephys'),
              dependencies={'Subject': subject.Subject,
                            'Session': Session,
                            'SkullReference': SkullReference,
                            'get_npx_data_dir': get_ephys_probe_data_dir,
                            'get_paramset_idx': get_paramset_idx,
                            'get_ks_data_dir': get_ks_data_dir})

# ---- Add neuropixels probes ----

for probe_type in ('neuropixels 1.0 - 3A', 'neuropixels 1.0 - 3B',
                   'neuropixels 2.0 - SS', 'neuropixels 2.0 - MS'):
    ephys.ProbeType.create_neuropixels_probe(probe_type)
