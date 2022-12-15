# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py_scripts//py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] tags=[]
# # Data Visualization

# +
import os

if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')

# -

import datajoint as dj
import datetime
from workflow_array_ephys.pipeline import ephys, probe, ephys_report

# +
# Get the unit key
unit_number = 13

unit_key = {'subject': 'subject6',
 'session_datetime': datetime.datetime(2021, 1, 15, 11, 16, 38),
 'insertion_number': 0,
 'paramset_idx': 0,
 'unit' : unit_number}

ephys.CuratedClustering.Unit & unit_key
# -

# ### Plot waveform
#

# +
from element_array_ephys.plotting.unit_level import plot_waveform, plot_auto_correlogram, plot_depth_waveforms

# Fetch unit data
sampling_rate = (ephys.EphysRecording & unit_key).fetch1(
    "sampling_rate") / 1e3  # in kHz

unit_data = (
    (ephys.CuratedClustering.Unit & unit_key) * ephys.WaveformSet.PeakWaveform
).fetch1()

waveform=unit_data["peak_electrode_waveform"]
spike_times=unit_data["spike_times"]

# Fetch unit data
plot_waveform(waveform, sampling_rate)
# -

# ### Plot autocorrelogram
#

# Plot Correlogram
plot_auto_correlogram(spike_times=spike_times, bin_size=0.001, window_size=1)

# ### Plot depth waveforms
#

# Plot depth Waveforms
plot_depth_waveforms(ephys, unit_key=unit_key, y_range=60)

# ## Probe level visualization
#

from element_array_ephys.plotting.probe_level import plot_driftmap

# ### Plot driftmap
#

# +
import matplotlib.pyplot as plt

probe_key = {'subject': 'subject6',
 'session_datetime': datetime.datetime(2021, 1, 15, 11, 16, 38),
 'insertion_number': 0,
 'paramset_idx': 0}

# Fetch all units recorded from the probe and specify the shank
units = ephys.CuratedClustering.Unit & probe_key & "cluster_quality_label='good'"
shank_no = 0

table = (
    units
    * ephys.ProbeInsertion
    * probe.ProbeType.Electrode
    & {"shank": shank_no}
)

spike_times, spike_depths = table.fetch(
    "spike_times", "spike_depths", order_by="unit"
)

plot_driftmap(spike_times, spike_depths, colormap="gist_heat_r")
plt.show()
# -

# ## Using ipywidget to visualize all probes & units from the database
#

# +
from element_array_ephys.plotting.widget import main

main(ephys)
