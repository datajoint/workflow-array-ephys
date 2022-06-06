# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: venv-nwb
#     language: python
#     name: venv-nwb
# ---

# + [markdown] tags=[]
# # DataJoint U24 - Workflow Array Electrophysiology

# + [markdown] tags=[]
# ## Setup
# -

# First, let's change directories to find the `dj_local_conf` file.

import os
# change to the upper level folder to detect dj_local_conf.json
if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')
assert os.path.basename(os.getcwd())=='workflow-array-ephys', ("Please move to the "
                                                               + "workflow directory")
# We'll be working with long tables, so we'll make visualization easier with a limit
import datajoint as dj; dj.config['display.limit']=10

# Next, we populate the python namespace with the required schemas

from workflow_array_ephys.pipeline import session, ephys, trial, event
from workflow_array_ephys import analysis

# + [markdown] jp-MarkdownHeadingCollapsed=true jp-MarkdownHeadingCollapsed=true tags=[]
# ## Trial and Event schemas
# -

# Tables in the `trial` and `event` schemas specify the structure of your experiment, including block, trial and event timing. 
# - Session has a 1-to-1 mapping with a behavior recording
# - A block is a continuous phase of an experiment that contains repeated instances of a condition, or trials. 
# - Events may occur within or outside of conditions, either instantaneous or continuous.
#
# The diagram below shows (a) the levels of hierarchy and (b) how the bounds may not completely overlap. A block may not fully capture trials and events may occur outside both blocks/trials.

# ```
# |----------------------------------------------------------------------------|
# |-------------------------------- Session ---------------------------------|__
# |-------------------------- BehaviorRecording -----------------------------|__
# |----- Block 1 -----|______|----- Block 2 -----|______|----- Block 3 -----|___
# | trial 1 || trial 2 |____| trial 3 || trial 4 |____| trial 5 |____| trial 6 |
# |_|e1|_|e2||e3|_|e4|__|e5|__|e6||e7||e8||e9||e10||e11|____|e12||e13|_________|
# |----------------------------------------------------------------------------|
# ```

# Let's load some example data. The `ingest.py` script has a series of loaders to help.

from workflow_array_ephys.ingest import ingest_subjects, ingest_sessions,\
                                        ingest_events, ingest_alignment

ingest_subjects(); ingest_sessions(); ingest_events()

# We have 100 total trials, either 'stim' or 'ctrl', with start and stop time

trial.Trial()

# Each trial is paired with one or more events that take place during the trial window.

trial.TrialEvent() & 'trial_id<5'

# Finally, the `AlignmentEvent` describes the event of interest and the window we'd like to see around it.

ingest_alignment()

event.AlignmentEvent()

# + [markdown] tags=[]
# ## Event-aligned spike times
# -

# First, we'll check that the data is still properly inserted from the previous notebooks.

ephys.CuratedClustering()

# For this example, we'll be looking at `subject6`.

clustering_key = (ephys.CuratedClustering 
                  & {'subject': 'subject6', 'session_datetime': '2021-01-15 11:16:38',
                     'insertion_number': 0}
                 ).fetch1('KEY')

trial.Trial & clustering_key

# And we can narrow our focus on `ctrl` trials.

ctrl_trials = trial.Trial & clustering_key & 'trial_type = "ctrl"'

# The `analysis` schema provides example tables to perform event-aligned spike-times analysis.

(dj.Diagram(analysis) + dj.Diagram(event.AlignmentEvent) + dj.Diagram(trial.Trial) + 
    dj.Diagram(ephys.CuratedClustering))

# + ***SpikesAlignmentCondition*** - a manual table to specify the inputs and condition for the analysis [markdown]
# Let's start by creating an analysis configuration - i.e. inserting into ***SpikesAlignmentCondition*** for the `center` event, called `center_button` in the `AlignmentEvent` table.

# + ***SpikesAlignment*** - a computed table to extract event-aligned spikes and compute unit PSTH
alignment_key = (event.AlignmentEvent & 'alignment_name = "center_button"'
                ).fetch1('KEY')
alignment_condition = {**clustering_key, **alignment_key, 
                       'trial_condition': 'ctrl_center_button'}
analysis.SpikesAlignmentCondition.insert1(alignment_condition, skip_duplicates=True)

analysis.SpikesAlignmentCondition.Trial.insert(
    (analysis.SpikesAlignmentCondition * ctrl_trials & alignment_condition).proj(),
    skip_duplicates=True)
# + a CuratedClustering of interest for analysis [markdown]
# With the steps above, we have created a new spike alignment condition for analysis, named `ctrl_center_button`, which retains all spiking information related to control trials during which the center button was pressed.

# + ***SpikesAlignment*** - a computed table to extract event-aligned spikes and compute unit PSTH
analysis.SpikesAlignmentCondition.Trial()
# + a set of trials of interest to perform the analysis on - `ctrl` trials [markdown]
# Now, let's create another set for the stimulus condition.
# + a set of trials of interest to perform the analysis on - `stim` trials
stim_trials = trial.Trial & clustering_key & 'trial_type = "stim"'
alignment_condition = {**clustering_key, **alignment_key, 'trial_condition': 'stim_center_button'}
analysis.SpikesAlignmentCondition.insert1(alignment_condition, skip_duplicates=True)
analysis.SpikesAlignmentCondition.Trial.insert(
    (analysis.SpikesAlignmentCondition * stim_trials & alignment_condition).proj(),
    skip_duplicates=True)

# + a set of trials of interest to perform the analysis on - `stim` trials [markdown]
# We can compare conditions in the `SpikesAlignmentCondition` table.

# + a set of trials of interest to perform the analysis on - `stim` trials
analysis.SpikesAlignmentCondition()

# + a set of trials of interest to perform the analysis on - `stim` trials
analysis.SpikesAlignmentCondition.Trial & 'trial_condition = "stim_center_button"'

# + a set of trials of interest to perform the analysis on - `stim` trials [markdown]
# ## Computation
#
# Now let's run the computation on these.

# + a set of trials of interest to perform the analysis on - `stim` trials
analysis.SpikesAlignment.populate(display_progress=True)

# + a set of trials of interest to perform the analysis on - `stim` trials [markdown]
# ## Visualize
#
# We can visualize the results with the `plot` function.

# + a set of trials of interest to perform the analysis on - `stim` trials
alignment_condition = {**clustering_key, **alignment_key, 'trial_condition': 'ctrl_center_button'}
analysis.SpikesAlignment().plot(alignment_condition, unit=2);

# + a set of trials of interest to perform the analysis on - `stim` trials
alignment_condition = {**clustering_key, **alignment_key, 'trial_condition': 'stim_center_button'}
analysis.SpikesAlignment().plot(alignment_condition, unit=2);
# -


