import json

from workflow_ephys.pipeline import subject, ephys

# ========== Insert new "Subject" ===========

subjects = [{'subject': 'dl56', 'sex': 'F', 'subject_birth_date': '2019-12-11 03:20:01'},
            {'subject': 'SC035', 'sex': 'F', 'subject_birth_date': '2019-02-16 03:20:01'},
            {'subject': 'SC038', 'sex': 'F', 'subject_birth_date': '2019-04-26 03:20:01'}]

subject.Subject.insert(subjects, skip_duplicates=True)

# ========== Insert new "ClusteringParamSet" for Suite2p ===========
with open('StandardConfig.json') as f:
    params = json.load(f)

ephys.ClusteringParamSet.insert_new_params('kilosort2', 0, 'Spike sorting using Kilosort2', params)
