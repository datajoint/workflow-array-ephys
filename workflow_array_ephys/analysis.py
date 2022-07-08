import datajoint as dj
import numpy as np

from .pipeline import db_prefix, ephys, trial, event

__all__ = ["db_prefix", "ephys", "trial", "event"]

schema = dj.schema(db_prefix + "analysis")


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
        unit_keys, unit_spike_times = (ephys.CuratedClustering.Unit & key).fetch(
            "KEY", "spike_times", order_by="unit"
        )
        bin_size = (SpikesAlignmentCondition & key).fetch1("bin_size")

        trialized_event_times = trial.get_trialized_alignment_event_times(
            key, trial.Trial & (SpikesAlignmentCondition.Trial & key)
        )

        min_limit = (trialized_event_times.event - trialized_event_times.start).max()
        max_limit = (trialized_event_times.end - trialized_event_times.event).max()

        # Spike raster
        aligned_trial_spikes = []
        units_spike_raster = {
            u["unit"]: {**key, **u, "aligned_spikes": []} for u in unit_keys
        }
        for _, r in trialized_event_times.iterrows():
            if np.isnan(r.event):
                continue
            alignment_start_time = r.event - min_limit
            alignment_end_time = r.event + max_limit
            for unit_key, spikes in zip(unit_keys, unit_spike_times):
                aligned_spikes = (
                    spikes[
                        (alignment_start_time <= spikes) & (spikes < alignment_end_time)
                    ]
                    - r.event
                )
                aligned_trial_spikes.append(
                    {
                        **key,
                        **unit_key,
                        **r.trial_key,
                        "aligned_spike_times": aligned_spikes,
                    }
                )
                units_spike_raster[unit_key["unit"]]["aligned_spikes"].append(
                    aligned_spikes
                )

        # PSTH
        for unit_spike_raster in units_spike_raster.values():
            spikes = np.concatenate(unit_spike_raster["aligned_spikes"])

            psth, edges = np.histogram(
                spikes, bins=np.arange(-min_limit, max_limit, bin_size)
            )
            unit_spike_raster["psth"] = (
                psth / len(unit_spike_raster.pop("aligned_spikes")) / bin_size
            )
            unit_spike_raster["psth_edges"] = edges[1:]

        self.insert1(key)
        self.AlignedTrialSpikes.insert(aligned_trial_spikes)
        self.UnitPSTH.insert(list(units_spike_raster.values()))

    def plot(self, key, unit, axs=None):
        import matplotlib.pyplot as plt
        from .plotting import plot_psth

        fig = None
        if axs is None:
            fig, axs = plt.subplots(2, 1, figsize=(12, 8))

        bin_size = (SpikesAlignmentCondition & key).fetch1("bin_size")
        trial_ids, aligned_spikes = (
            self.AlignedTrialSpikes & key & {"unit": unit}
        ).fetch("trial_id", "aligned_spike_times")
        psth, psth_edges = (self.UnitPSTH & key & {"unit": unit}).fetch1(
            "psth", "psth_edges"
        )

        xlim = psth_edges[0], psth_edges[-1]

        plot_psth._plot_spike_raster(
            aligned_spikes,
            trial_ids=trial_ids,
            ax=axs[0],
            title=f"{dict(**key, unit=unit)}",
            xlim=xlim,
        )
        plot_psth._plot_psth(psth, psth_edges, bin_size, ax=axs[1], title="", xlim=xlim)

        return fig
