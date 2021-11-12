from workflow_array_ephys.pipeline import ephys


def run(display_progress=True):

    populate_settings = {'display_progress': display_progress,
                         'reserve_jobs': False,
                         'suppress_errors': True}

    print('\n---- Populate ephys.EphysRecording ----')
    ephys.EphysRecording.populate(**populate_settings)

    print('\n---- Populate ephys.LFP ----')
    ephys.LFP.populate(**populate_settings)

    print('\n---- Populate ephys.Clustering ----')
    ephys.Clustering.populate(**populate_settings)

    print('\n---- Populate ephys.CuratedClustering ----')
    ephys.CuratedClustering.populate(**populate_settings)

    print('\n---- Populate ephys.WaveformSet ----')
    ephys.WaveformSet.populate(**populate_settings)


if __name__ == '__main__':
    run()
