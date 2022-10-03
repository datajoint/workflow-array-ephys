import datetime
import pathlib

import datetime
import datajoint as dj
import importlib
import inspect
import typing as T
from .plotting.ephys import *

schema = dj.schema()

_linking_module = None


def activate(
    schema_name, *, create_schema=True, create_tables=True, linking_module=None
):
    """
    activate(schema_name, *, create_schema=True, create_tables=True,
             linking_module=None)
        :param schema_name: schema name on the database server to activate the
                            `subject` element
        :param create_schema: when True (default), create schema in the
                              database if it does not yet exist.
        :param create_tables: when True (default), create tables in the
                              database if they do not yet exist.
        :param linking_module: a module name or a module containing the
         required dependencies
    """
    if isinstance(linking_module, str):
        linking_module = importlib.import_module(linking_module)
    assert inspect.ismodule(linking_module), (
        "The argument 'dependency' must " + "be a module's name or a module"
    )

    global _linking_module
    _linking_module = linking_module

    schema.activate(
        schema_name,
        create_schema=create_schema,
        create_tables=create_tables,
        add_objects=linking_module.__dict__,
    )


@schema
class ProbeLevelReport(dj.Computed):
    definition = """
    -> ephys.CuratedClustering
    ---
    drift_map_plot: attach
    """

    def make(self, key):

        spike_times, spike_depths = (
            _linking_module.ephys.CuratedClustering.Unit
            & key
            & "cluster_quality_label='good'"
        ).fetch("spike_times", "spike_depths", order_by="unit")

        # Get the figure
        fig = plot_driftmap(spike_times, spike_depths, colormap="gist_heat_r")
        fig_prefix = "-".join(
            [
                v.strftime("%Y%m%d%H%M%S")
                if isinstance(v, datetime.datetime)
                else str(v)
                for v in key.values()
            ]
        )

        # Save fig and insert
        save_dir = _make_save_dir()
        fig_dict = _save_figs(
            figs=(fig,),
            fig_names=("drift_map_plot",),
            save_dir=save_dir,
            fig_prefix=fig_prefix,
            extension=".png",
        )

        self.insert1({**key, **fig_dict})


@schema
class UnitLevelReport(dj.Computed):
    definition = """
    -> ephys.CuratedClustering.Unit
    ---
    waveform_plot:         attach
    autocorrelogram_plot:  attach
    """

    def make(self, key):

        sampling_rate = (_linking_module.ephys.EphysRecording & key).fetch1(
            "sampling_rate"
        ) / 1e3  # in kHz

        peak_electrode_waveform, spike_times = (
            _linking_module.ephys.CuratedClustering.Unit
            * _linking_module.ephys.WaveformSet.PeakWaveform
            & "cluster_quality_label='good'"
            & key
        ).fetch1("peak_electrode_waveform", "spike_times")

        # Get the figure
        fig_waveform = plot_waveform(
            waveform=peak_electrode_waveform, sampling_rate=sampling_rate
        )
        fig_correlogram = plot_correlogram(
            spike_times=spike_times, bin_size=0.001, window_size=1
        )

        fig_prefix = "-".join(
            [
                v.strftime("%Y%m%d%H%M%S")
                if isinstance(v, datetime.datetime)
                else str(v)
                for v in key.values()
            ]
        )

        # Save fig and insert
        save_dir = _make_save_dir()

        fig_dict = _save_figs(
            figs=(fig_waveform, fig_correlogram),
            fig_names=("waveform_plot", "autocorrelogram_plot"),
            save_dir=save_dir,
            fig_prefix=fig_prefix,
            extension=".png",
        )

        self.insert1({**key, **fig_dict})


def _make_save_dir() -> pathlib.Path:

    if "store" not in dj.config:
        root_dir = pathlib.Path(dj.config["custom"]["ephys_root_data_dir"])
        dj.config["stores"] = {
            "djstore": {
                "protocol": "file",
                "location": f"{root_dir}/figures",
                "stage": f"{root_dir}/figures",
            }
        }
        dj.config.save_local()
    save_dir = pathlib.Path(dj.config["stores"]["djstore"]["stage"])
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def _save_figs(
    figs, fig_names, save_dir, fig_prefix, extension=".png"
) -> T.Dict[str, pathlib.Path]:
    fig_dict = {}
    for fig, fig_name in zip(figs, fig_names):
        fig_filepath = save_dir / (fig_prefix + "_" + fig_name + extension)
        fig.tight_layout()
        fig.savefig(fig_filepath)
        fig_dict[fig_name] = fig_filepath.as_posix()

    return fig_dict
