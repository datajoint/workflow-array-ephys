import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import datajoint as dj
import pathlib
from ..pipeline import ephys, probe


def plot_raster(units, spike_times) -> matplotlib.figure.Figure:

    units = np.arange(1, len(units) + 1)
    x = np.hstack(spike_times)
    y = np.hstack([np.full_like(s, u) for u, s in zip(units, spike_times)])
    fig, ax = plt.subplots(1, 1, figsize=(32, 8), dpi=100)
    ax.plot(x, y, "|")
    ax.set(
        xlabel="Time (s)",
        ylabel="Unit",
        xlim=[0 - 0.5, x[-1] + 0.5],
        ylim=(1, len(units)),
    )
    sns.despine()
    fig.tight_layout()

    return fig


def plot_driftmap(
    spike_times: np.ndarray, spike_depths: np.ndarray, colormap="gist_heat_r"
) -> matplotlib.figure.Figure:

    spike_times = np.hstack(spike_times)
    spike_depths = np.hstack(spike_depths)

    # Time-depth 2D histogram
    time_bin_count = 1000
    depth_bin_count = 200

    spike_bins = np.linspace(0, spike_times.max(), time_bin_count)
    depth_bins = np.linspace(0, np.nanmax(spike_depths), depth_bin_count)

    spk_count, spk_edges, depth_edges = np.histogram2d(
        spike_times, spike_depths, bins=[spike_bins, depth_bins]
    )
    spk_rates = spk_count / np.mean(np.diff(spike_bins))
    spk_edges = spk_edges[:-1]
    depth_edges = depth_edges[:-1]

    # Canvas setup
    fig = plt.figure(figsize=(12, 5), dpi=200)
    grid = plt.GridSpec(15, 12)

    ax_cbar = plt.subplot(grid[0, 0:10])
    ax_driftmap = plt.subplot(grid[2:, 0:10])
    ax_spkcount = plt.subplot(grid[2:, 10:])

    # Plot main
    im = ax_driftmap.imshow(
        spk_rates.T,
        aspect="auto",
        cmap=colormap,
        extent=[spike_bins[0], spike_bins[-1], depth_bins[-1], depth_bins[0]],
    )
    # Cosmetic
    ax_driftmap.invert_yaxis()
    ax_driftmap.set(
        xlabel="Time (s)",
        ylabel="Distance from the probe tip ($\mu$m)",
        ylim=[depth_edges[0], depth_edges[-1]],
    )

    # Colorbar for firing rates
    cb = fig.colorbar(im, cax=ax_cbar, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.xaxis.tick_top()
    cb.set_label("Firing rate (Hz)")
    cb.ax.xaxis.set_label_position("top")

    # Plot spike count
    ax_spkcount.plot(spk_count.sum(axis=0) / 10e3, depth_edges, "k")
    ax_spkcount.set_xlabel("Spike count (x$10^3$)")
    ax_spkcount.set_yticks([])
    ax_spkcount.set_ylim(depth_edges[0], depth_edges[-1])
    sns.despine()

    return fig


def plot_waveform(
    waveform: np.array, sampling_rate: float, fig=None, ax=None
) -> matplotlib.figure.Figure:

    waveform_df = pd.DataFrame(data={"waveform": waveform})
    waveform_df["timestamp"] = waveform_df.index / sampling_rate
    waveform_df.set_index("timestamp", inplace=True)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(3, 3))

    ax.plot(waveform_df, "k")
    ax.set(xlabel="Time (ms)", ylabel="Voltage ($\mu$V)", title="Avg. waveform")
    sns.despine()

    return fig


def plot_correlogram(
    spike_times, bin_size=0.001, window_size=1, fig=None, ax=None
) -> matplotlib.figure.Figure:

    from brainbox.singlecell import acorr

    correlogram = acorr(
        spike_times=spike_times, bin_size=bin_size, window_size=window_size
    )
    df = pd.DataFrame(
        data={"correlogram": correlogram},
        index=pd.RangeIndex(
            start=-(window_size * 1e3) / 2,
            stop=(window_size * 1e3) / 2 + bin_size * 1e3,
            step=bin_size * 1e3,
        ),
    )

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(3, 3))

    df["lags"] = df.index  # in ms

    ax.plot(df["lags"], df["correlogram"], color="royalblue", linewidth=0.5)
    ymax = round(correlogram.max() / 10) * 10
    ax.set_ylim(0, ymax)
    # ax.axvline(x=0, color="k", linewidth=0.5, ls="--")
    ax.set(xlabel="Lags (ms)", ylabel="Count", title="Auto Correlogram")
    sns.despine()

    return fig


def plot_depth_waveforms(
    probe_type: str,
    unit_id: int,
    sampling_rate: float,
    y_range: float = 50,
    fig=None,
    ax=None,
):

    peak_electrode = (ephys.CuratedClustering.Unit & f"unit={unit_id}").fetch1(
        "electrode"
    )  # electrode where the peak waveform was found

    peak_coord_y = (
        probe.ProbeType.Electrode()
        & f"probe_type='{probe_type}'"
        & f"electrode={peak_electrode}"
    ).fetch1("y_coord")

    coord_y = (probe.ProbeType.Electrode).fetch(
        "y_coord"
    )  # y-coordinate for all electrodes
    coord_ylim_low = (
        coord_y.min()
        if (peak_coord_y - y_range) <= coord_y.min()
        else peak_coord_y - y_range
    )
    coord_ylim_high = (
        coord_y.max()
        if (peak_coord_y + y_range) >= coord_y.max()
        else peak_coord_y + y_range
    )

    tbl = (
        (probe.ProbeType.Electrode)
        & f"probe_type = '{probe_type}'"
        & f"y_coord BETWEEN {coord_ylim_low} AND {coord_ylim_high}"
    )
    electrodes_to_plot = tbl.fetch("electrode")

    coords = np.array(tbl.fetch("x_coord", "y_coord")).T  # x, y coordinates

    waveforms = (
        ephys.WaveformSet.Waveform
        & f"unit = {unit_id}"
        & f"electrode IN {tuple(electrodes_to_plot)}"
    ).fetch("waveform_mean")
    waveforms = np.stack(waveforms)  # all mean waveforms of a given neuron

    if ax is None:
        fig, ax = plt.subplots(1, 1, frameon=True, figsize=[1.5, 2], dpi=200)

    x_min, x_max = np.min(coords[:, 0]), np.max(coords[:, 0])
    y_min, y_max = np.min(coords[:, 1]), np.max(coords[:, 1])

    # Spacing between channels (in um)
    x_inc = np.abs(np.diff(coords[:, 0])).min()
    y_inc = np.unique((np.abs(np.diff(coords[:, 1])))).max()

    time = np.arange(waveforms.shape[1]) * (1 / sampling_rate)

    x_scale_factor = x_inc / (time + (1 / sampling_rate))[-1]
    time_scaled = time * x_scale_factor

    wf_amps = waveforms.max(axis=1) - waveforms.min(axis=1)
    max_amp = wf_amps.max()
    y_scale_factor = y_inc / max_amp

    unique_x_loc = np.sort(np.unique(coords[:, 0]))
    xtick_label = list(map(str, map(int, unique_x_loc)))
    xtick_loc = time_scaled[int(len(time_scaled) / 2) + 1] + unique_x_loc

    # Plot the mean waveform for each electrode
    for electrode, wf, coord in zip(electrodes_to_plot, waveforms, coords):

        wf_scaled = wf * y_scale_factor
        wf_scaled -= wf_scaled.mean()

        color = "r" if electrode == peak_electrode else [0.2, 0.3, 0.8] * 255
        ax.plot(
            time_scaled + coord[0], wf_scaled + coord[1], color=color, linewidth=0.5
        )

    ax.set(xlabel="($\mu$m)", ylabel="Distance from the probe tip ($\mu$m)")
    ax.set_ylim([y_min - y_inc * 2, y_max + y_inc * 2])
    ax.xaxis.get_label().set_fontsize(8)
    ax.yaxis.get_label().set_fontsize(8)
    ax.tick_params(axis="both", which="major", labelsize=7)
    ax.set_xticks(xtick_loc)
    ax.set_xticklabels(xtick_label)
    sns.despine()
    sns.set_style("white")

    return fig
