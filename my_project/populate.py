import numpy as np
from my_project import ephys

populate_settings = {'reserve_jobs': True, 'suppress_errors': True, 'display_progress': True}


def populate():
    # populate "dj.Imported" and "dj.Computed" tables
    for tbl in ephys._table_classes:
        if np.any([c.__name__ in ('Imported', 'Computed') for c in tbl.__bases__]):
            print('\n--- Populating {} ---'.format(tbl.__name__))
            tbl.populate(**populate_settings)


if __name__ == '__main__':
    populate()
