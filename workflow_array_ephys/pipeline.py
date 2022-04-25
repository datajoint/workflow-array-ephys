import datajoint as dj

from element_lab import lab
from element_animal import subject
from element_session import session_with_datetime as session
from element_array_ephys import probe
from element_array_ephys import ephys_acute as ephys

from element_lab.lab import Source, Lab, Protocol, User, Project
from element_animal.subject import Subject
from element_session.session_with_datetime import Session

from .paths import get_ephys_root_data_dir, get_session_directory

if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')


# Activate "lab", "subject", "session" schema ------------------------------------------

lab.activate(db_prefix + 'lab')

subject.activate(db_prefix + 'subject', linking_module=__name__)

Experimenter = lab.User
session.activate(db_prefix + 'session', linking_module=__name__)


# Declare table "SkullReference" for use in element-array-ephys ------------------------

@lab.schema
class SkullReference(dj.Lookup):
    definition = """
    skull_reference   : varchar(60)
    """
    contents = zip(['Bregma', 'Lambda'])


# Activate "ephys" schema --------------------------------------------------------------

ephys.activate(db_prefix + 'ephys', 
               db_prefix + 'probe', 
               linking_module=__name__)