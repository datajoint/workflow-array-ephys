from asyncio import AbstractChildWatcher
import datajoint as dj
from matplotlib.category import UnitData
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go
from ipywidgets import widgets as wg
from plotly.subplots import make_subplots
from workflow_array_ephys.pipeline import subject, session, ephys, probe

# Fetch unit data
insertion_number = 0
unit_id = 88

sampling_rate = (ephys.EphysRecording & f"insertion_number={insertion_number}").fetch1(
    "sampling_rate"
) / 1e3  # in kHz

unit_data = (
    ephys.CuratedClustering.Unit * ephys.WaveformSet.PeakWaveform & f"unit = {unit_id}"
).fetch1()

# Fetch all electrodes and waveform for a given unit
used_electrodes, waveforms = (ephys.WaveformSet.Waveform & f"unit = {unit_id}").fetch(
    "electrode", "waveform_mean"
)
waveforms = np.stack(waveforms)  # all mean waveforms of a given neuron

# probe coordinate info
electrodes = (probe.ProbeType.Electrode() & "probe_type='neuropixels 1.0 - 3B'").fetch(
    "electrode"
)

coords = np.array(
    (probe.ProbeType.Electrode() & "probe_type='neuropixels 1.0 - 3B'").fetch(
        "x_coord", "y_coord"
    )
).T  # x, y coordinates
coords = coords[used_electrodes, :]  # coordinate for the used electrodes

fig, ax = plt.subplots(1, 1, frameon=True, figsize=[1.5, 5], dpi=100)

x_min, x_max = np.min(coords[:, 0]), np.max(coords[:, 0])
y_min, y_max = np.min(coords[:, 1]), np.max(coords[:, 1])

# Spacing between channels (in um)
x_inc = np.abs(np.diff(coords[:, 0])).min()
y_inc = np.unique((np.abs(np.diff(coords[:, 1])))).max()

# number of unique positions
n_xpos, n_ypos = len(set(coords[:, 0])), len(set(coords[:, 1]))
# time_len = np.shape(waveforms)[0]

# # time (in ms) * x_scale (in um/ms) + x_start(coord[0]) = position
# # the waveform takes 0.9 of each x interval between adjacent channels
# dt = 1 / 30
# x_scale = (x_max - x_min) / (n_xpos - 1) * 0.9 / (dt * time_len)

# # y_scale adjusted with the amplitude of the waveforms
# # waveform voltage in (uV) * y_scale (in um/uV) + y_start (coord[1]) = position
# waveform_peak = np.max(abs(waveforms))
# # peak waveform takes 2 times of each y interval between adjacent channels
# y_scale = (y_max - y_min) / (n_ypos - 1) / waveform_peak * 5

time = np.arange(waveforms.shape[1]) * (1 / sampling_rate)

x_scale_factor = x_inc / (time + (1 / sampling_rate))[-1]
time_scaled = time * x_scale_factor

wf_amps = waveforms.max(axis=1) - waveforms.min(axis=1)
max_amp = wf_amps.max()
y_scale_factor = y_inc / max_amp

for wf, coord in zip(waveforms, coords):

    wf_scaled = wf * y_scale_factor
    wf_scaled -= wf_scaled.mean()

    ax.plot(
        time_scaled + coord[0],
        wf_scaled + coord[1],
        color=[0.2, 0.3, 0.8],
        linewidth=0.2,
    )
    break
