import datajoint as dj
from workflow_ephys.pipeline import ephys

populate_settings = {'reserve_jobs': True, 'suppress_errors': True, 'display_progress': True}


def populate():
    # populate "dj.Imported" and "dj.Computed" tables
    for name in dir(ephys):
        attr = getattr(ephys, name)
        if isinstance(attr, dj.user_tables.OrderedClass):
            if isinstance(attr(), (dj.Imported, dj.Computed)):
                print('\n--- Populating {} ---'.format(attr.__name__))
                attr.populate(**populate_settings)


if __name__ == '__main__':
    populate()
