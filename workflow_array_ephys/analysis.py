import datajoint as dj
import numpy as np

from .pipeline import db_prefix, ephys, trial, event


schema = dj.schema(db_prefix + 'analysis')


@schema
class SpikesAlignmentCondition(dj.Manual):
    definition = """
    -> ephys.CuratedClustering
    -> event.AlignmentEvent
    trial_condition: varchar(128) # user-friendly name of condition
    ---
    condition_description='': varchar(1000)
    bin_size=0.04: float # bin-size (in second) used to compute the PSTH
    """

    class Trial(dj.Part):
        definition = """  # Trials on which to compute event-aligned spikes and PSTH
        -> master
        -> trial.Trial
        """


@schema
class SpikesAlignment(dj.Computed):
    definition = """
    -> SpikesAlignmentCondition
    -> ephys.CuratedClustering
    """

    class AlignedTrialSpikes(dj.Part):
        definition = """
        -> master
        -> ephys.CuratedClustering.Unit
        -> SpikesAlignmentCondition.Trial
        ---
        aligned_spike_times: longblob # (s) spike times relative to alignment event time
        """

    class UnitPSTH(dj.Part):
        definition = """
        -> master
        -> ephys.CuratedClustering.Unit
        ---
        psth: longblob  # event-aligned spike peristimulus time histogram (PSTH)
        psth_edges: longblob  
        """

    def make(self, key):
        unit_keys, unit_spike_times = (ephys.CuratedClustering.Unit & key
                                       ).fetch('KEY', 'spike_times', order_by='unit')

        trial_keys, trial_starts, trial_ends = (trial.Trial
                                                & (SpikesAlignmentCondition.Trial & key)
                                                ).fetch(
            'KEY', 'trial_start_time', 'trial_stop_time', order_by='trial_id')

        bin_size = (SpikesAlignmentCondition & key).fetch1('bin_size')

        alignment_spec = (event.AlignmentEvent & key).fetch1()

        # Spike raster
        aligned_trial_spikes = []
        units_spike_raster = {u['unit']: {**key, **u, 'aligned_spikes': []
                                          } for u in unit_keys}
        min_limit, max_limit = np.Inf, -np.Inf
        for trial_key, trial_start, trial_stop in zip(trial_keys, trial_starts,
                                                      trial_ends):
            alignment_event_time = (event.Event & key
                                    & {'event_type':
                                       alignment_spec['alignment_event_type']}
                                    & (f'event_start_time BETWEEN {trial_start} '
                                       + f'AND {trial_stop}')
                                    )
            if alignment_event_time:
                # if multiple of such alignment event, pick the last one in the trial
                alignment_event_time = alignment_event_time.fetch(
                    'event_start_time', order_by='event_start_time DESC', limit=1)[0]
            else:
                continue

            alignment_start_time = (event.Event & key
                                    & {'event_type': alignment_spec['start_event_type']}
                                    & f'event_start_time < {alignment_event_time}')
            if alignment_start_time:
                # if multiple start events, pick immediately prior to alignment event
                alignment_start_time = alignment_start_time.fetch(
                    'event_start_time', order_by='event_start_time DESC', limit=1)[0]
                alignment_start_time = max(alignment_start_time, trial_start)
            else:
                alignment_start_time = trial_start

            alignment_end_time = (event.Event & key
                                  & {'event_type': alignment_spec['end_event_type']}
                                  & f'event_start_time > {alignment_event_time}')
            if alignment_end_time:
                # if multiple start events, pick immediatly following alignment event
                alignment_end_time = alignment_end_time.fetch(
                    'event_start_time', order_by='event_start_time', limit=1)[0]
                alignment_end_time = min(alignment_end_time, trial_stop)
            else:
                alignment_end_time = trial_stop

            alignment_event_time += alignment_spec['alignment_time_shift']
            alignment_start_time += alignment_spec['start_time_shift']
            alignment_end_time += alignment_spec['end_time_shift']

            min_limit = min(alignment_start_time - alignment_event_time, min_limit)
            max_limit = max(alignment_end_time - alignment_event_time, max_limit)

            for unit_key, spikes in zip(unit_keys, unit_spike_times):
                aligned_spikes = spikes[(alignment_start_time <= spikes)
                                        & (spikes < alignment_end_time)
                                        ] - alignment_event_time
                aligned_trial_spikes.append({**key, **unit_key, **trial_key,
                                             'aligned_spike_times': aligned_spikes})
                units_spike_raster[unit_key['unit']]['aligned_spikes'
                                                     ].append(aligned_spikes)

        # PSTH
        for unit_spike_raster in units_spike_raster.values():
            spikes = np.concatenate(unit_spike_raster['aligned_spikes'])

            psth, edges = np.histogram(spikes,
                                       bins=np.arange(min_limit, max_limit, bin_size))
            unit_spike_raster['psth'] = (psth /
                                         len(unit_spike_raster.pop('aligned_spikes')
                                             ) / bin_size)
            unit_spike_raster['psth_edges'] = edges[1:]

        self.insert1(key)
        self.AlignedTrialSpikes.insert(aligned_trial_spikes)
        self.UnitPSTH.insert(list(units_spike_raster.values()))

    def plot_raster(self, key, unit, axs=None):
        import matplotlib.pyplot as plt
        from .plotting import plot_psth

        fig = None
        if axs is None:
            fig, axs = plt.subplots(2, 1, figsize=(12, 8))

        trial_ids, aligned_spikes = (self.AlignedTrialSpikes
                                     & key & {'unit': unit}
                                     ).fetch('trial_id', 'aligned_spike_times')
        psth, psth_edges = (self.UnitPSTH & key & {'unit': unit}).fetch1(
            'psth', 'psth_edges')

        xlim = psth_edges[0], psth_edges[-1]

        plot_psth._plot_spike_raster(aligned_spikes, trial_ids=trial_ids, ax=axs[0],
                                     title=f'{dict(**key, unit=unit)}', xlim=xlim)
        plot_psth._plot_psth(psth, psth_edges, ax=axs[1],
                             title='', xlim=xlim)

        return fig
