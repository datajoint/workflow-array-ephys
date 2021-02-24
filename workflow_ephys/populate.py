from workflow_ephys.pipeline import ephys


def populate(display_progress=True):

    populate_settings = {'display_progress': display_progress, 'reserve_jobs': False, 'suppress_errors': True}

    print('\n---- Populate ephys.EphysRecording ----')
    ephys.EphysRecording.populate(**populate_settings)

    print('\n---- Populate ephys.LFP ----')
    ephys.LFP.populate(**populate_settings)

    print('\n---- Populate ephys.Clustering ----')
    ephys.Clustering.populate(**populate_settings)

    print('\n---- Populate ephys.Waveform ----')
    ephys.Waveform.populate(**populate_settings)


if __name__ == '__main__':
    populate()
