import datajoint as dj
from workflow_ephys.pipeline import ephys

populate_settings = {'reserve_jobs': True, 'suppress_errors': True, 'display_progress': True}


def populate():
    ephys.EphysRecording.populate(**populate_settings)
    ephys.LFP.populate(**populate_settings)
    ephys.ClusteringTask.populate(**populate_settings)
    ephys.Clustering.populate(**populate_settings)
    ephys.Waveform.populate(**populate_settings)


if __name__ == '__main__':
    populate()
