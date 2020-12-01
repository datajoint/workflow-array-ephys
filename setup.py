from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

long_description = """"
# Pipeline for extracellular electrophysiology using Neuropixels probe and kilosort clustering method

Build a full ephys pipeline using the DataJoint elements
+ [elements-lab](https://github.com/datajoint/elements-lab)
+ [elements-animal](https://github.com/datajoint/elements-animal)
+ [elements-ephys](https://github.com/datajoint/elements-ephys)
"""

with open(path.join(here, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name='workflow_ephys-ephys',
    version='0.0.1',
    description="Extracellular electrophysiology pipeline using the DataJoint elements",
    long_description=long_description,
    author='DataJoint NEURO',
    author_email='info@vathes.com',
    license='MIT',
    url='https://github.com/datajoint/workflow-ephys',
    keywords='neuroscience datajoint ephys',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=requirements,
)
