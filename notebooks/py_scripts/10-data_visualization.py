# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py_scripts//py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.9.13 ('ele')
#     language: python
#     name: python3
# ---

# + [markdown] tags=[]
# # Data Visualization
# -

# This notebook is intended to demonstrate the use of visualization functions for ephys data and datajoint tables for storing the results.

import os

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")

# Visualization results (e.g., figures) will be stored in tables created under the `ephys_report` schema. By default, the schema will be activated with the `ephys` schema.

import datajoint as dj
import datetime
from workflow_array_ephys.pipeline import ephys, probe, ephys_report

# First, we fetch one example unit data from the `ephys.CuratedClustering.Unit` table that will be used for this demonstration.

# +
# Get the unit key
unit_number = 13

unit_key = {
    "subject": "subject6",
    "session_datetime": datetime.datetime(2021, 1, 15, 11, 16, 38),
    "insertion_number": 0,
    "paramset_idx": 0,
    "unit": unit_number,
}

ephys.CuratedClustering.Unit & unit_key
# -

# Figures can be generated either at the probe level or a single unit level. Here we start start with the unit-level visualization and import functions from `element_array_ephys.plotting.unit_level`

# ## Unit level visualization
#

# - There are functions to plot the 1) **unit waveform**, 2) **autocorrelogram**, and 3) **depth waveforms** which plot the peak waveform as well as waveforms detected from neighboring sites from a given probe.
#
# - Each figure was plotted with the *plotly* library to allow interactive exploration of the data.

# ### Plot waveform
#

# +
from element_array_ephys.plotting.unit_level import (
    plot_waveform,
    plot_auto_correlogram,
    plot_depth_waveforms,
)

# Fetch unit data
sampling_rate = (ephys.EphysRecording & unit_key).fetch1(
    "sampling_rate"
) / 1e3  # in kHz

unit_data = (
    (ephys.CuratedClustering.Unit & unit_key) * ephys.WaveformSet.PeakWaveform
).fetch1()

waveform = unit_data["peak_electrode_waveform"]
spike_times = unit_data["spike_times"]

# Fetch unit data
plot_waveform(waveform, sampling_rate)
# -

# ### Plot autocorrelogram
#

# Plot Correlogram
plot_auto_correlogram(spike_times=spike_times, bin_size=0.001, window_size=1)

# ### Plot depth waveforms
#

# The electrode site where the peak waveform was found will be plotted in red. The `y_range` parameter can be modified to alter the vertical range in which the neighboring waveforms are found.

# Plot depth Waveforms
plot_depth_waveforms(ephys, unit_key=unit_key, y_range=60)

# ## Probe level visualization
#

# At the probe level, we plot a driftmap to visualize the activity of all neurons recorded on that probe per shank. Here we import the function from `element_array_ephys.plotting.probe_level`

from element_array_ephys.plotting.probe_level import plot_driftmap

# ### Plot driftmap
#

# - Specify the probe key and the shank from that probe. Fetch `spikes_times` and `spike_depths` from all units from the shank, which will be used as an input argument for the function `plot_driftmap`.
#
# - Units are aligned relative to the distance from the probe tip. An increase in activity (firing rates) is indicated by dark red.

# +
import matplotlib.pyplot as plt

probe_key = {
    "subject": "subject6",
    "session_datetime": datetime.datetime(2021, 1, 15, 11, 16, 38),
    "insertion_number": 0,
    "paramset_idx": 0,
}

# Fetch all units recorded from the probe and specify the shank
units = ephys.CuratedClustering.Unit & probe_key & "cluster_quality_label='good'"
shank_no = 0

table = units * ephys.ProbeInsertion * probe.ProbeType.Electrode & {"shank": shank_no}

spike_times, spike_depths = table.fetch("spike_times", "spike_depths", order_by="unit")

plot_driftmap(spike_times, spike_depths, colormap="gist_heat_r")
plt.show()
# -

# ## Using ipywidget to visualize all probes & units ingested into datajoint tables

# Here, all of the above plots were packaged into a single widget, which can be imported as follows:

# +
from element_array_ephys.plotting.widget import main

main(ephys)
# -

# You can select a probe & shank and all the individual units associated with them via dropdown and it will automatically fetch & render the plot stored in tables from the `ephys_report` schema.
