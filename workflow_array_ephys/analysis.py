import datajoint as dj
import numpy as np

from .pipeline import db_prefix, session, ephys, trial, event


schema = dj.schema(db_prefix + 'analysis')


@schema
class SpikesAlignmentCondition(dj.Manual):
    definition = """
    -> ephys.CuratedClustering
    -> event.AlignmentEvent
    trial_condition: varchar(128) # user-friendly name of condition
    ---
    bin_size=0.04: float # bin-size (in second) used to compute the PSTH
    """

    class Trial(dj.Part):
        definition = """  # Trials (or subset of trials) to computed event-aligned spikes and PSTH on 
        -> master
        -> trial.Trial
        """


@schema
class SpikesAlignment(dj.Computed):
    definition = """
    -> SpikesAlignmentCondition
    -> ephys.CuratedClustering.Unit
    """

    class AlignedTrialSpikes(dj.Part):
        definition = """
        -> master
        -> SpikesAlignmentCondition.Trial
        ---
        aligned_spike_times: longblob  # (s) spike times relative to the alignment event time
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
        unit_keys, unit_spike_times = (ephys.CuratedClustering.Unit & key).fetch('KEY', 'unit_spike_times', order_by='unit')

        trial_keys, trial_starts, trial_ends = (trial.Trial & (SpikesAlignmentCondition.Trial & key)).fetch(
            'KEY', 'trial_start_time', 'trial_stop_time', order_by='trial_id')

        bin_size = (SpikesAlignmentCondition & key).fetch1('bin_size')

        alignment_spec = (event.AlignmentEvent & key).fetch1()

        # Spike raster
        aligned_trial_spikes = []
        units_spike_raster = {u['unit']: {'KEY': {}, 'aligned_spikes': []} for u in unit_keys}
        min_limit, max_limit = np.Inf, -np.Inf
        for trial_key, trial_start, trial_stop in zip(trial_keys, trial_starts, trial_ends):
            alignment_event_time = (event.Event & key & {'event_type': alignment_spec['alignment_event_type']}
                                    & f'event_start_time BETWEEN {trial_start} AND {trial_stop}')
            if alignment_event_time:
                # if there are multiple of such alignment event, pick the last one in the trial
                alignment_event_time = alignment_event_time.fetch(
                    'event_start_time', order_by='event_start_time DESC', limit=1)[0]
            else:
                continue

            alignment_start_time = (event.Event & key & {'event_type': alignment_spec['start_event_type']}
                                    & f'event_start_time < {alignment_event_time}')
            if alignment_start_time:
                # if there are multiple of such start event, pick the most immediate one prior to the alignment event
                alignment_start_time = alignment_start_time.fetch(
                    'event_start_time', order_by='event_start_time DESC', limit=1)[0]
                alignment_start_time = max(alignment_start_time, trial_start)
            else:
                alignment_start_time = trial_start

            alignment_end_time = (event.Event & key & {'event_type': alignment_spec['end_event_type']}
                                  & f'event_start_time > {alignment_event_time}')
            if alignment_end_time:
                # if there are multiple of such start event, pick the most immediate one following the alignment event
                alignment_end_time = alignment_end_time.fetch(
                    'event_start_time', order_by='event_start_time', limit=1)[0]
                alignment_end_time = min(alignment_end_time, trial_stop)
            else:
                alignment_end_time = trial_stop

            alignment_event_time += alignment_spec['alignment_time_shift']
            alignment_start_time += alignment_spec['start_time_shift']
            alignment_end_time += alignment_spec['end_time_shift']

            min_limit = min(alignment_start_time, min_limit)
            max_limit = max(alignment_end_time, max_limit)

            for unit_key, spikes in zip(unit_keys, unit_spike_times):
                aligned_spikes = spikes[(alignment_start_time <= spikes)
                                        & (spikes < alignment_end_time)] - alignment_event_time
                aligned_trial_spikes.append({**key, **unit_key, **trial_key, 'aligned_spike_times': aligned_spikes})
                units_spike_raster[unit_key['unit']]['aligned_spikes'].append(aligned_spikes)

        # PSTH
        for unit_spike_raster in units_spike_raster.values():
            spikes = np.concatenate(unit_spike_raster['aligned_spikes'])

            psth, edges = np.histogram(spikes, bins=np.arange(min_limit, max_limit, bin_size))
            unit_spike_raster['psth'] = psth / len(unit_spike_raster.pop('aligned_spikes')) / bin_size
            unit_spike_raster['psth_edges'] = edges[1:]

        self.insert1(key)
        self.AlignedTrialSpikes.insert(aligned_trial_spikes)
        self.UnitPSTH.insert(list(units_spike_raster.values()))
