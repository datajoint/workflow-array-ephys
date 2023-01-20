from os import path

from setuptools import find_packages, setup

pkg_name = "workflow_array_ephys"
here = path.abspath(path.dirname(__file__))

long_description = """"
# Pipeline for extracellular electrophysiology using Neuropixels probe and kilosort clustering method

Build a full ephys pipeline using the DataJoint elements
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-array-ephys](https://github.com/datajoint/element-array-ephys)
"""

with open(path.join(here, "requirements.txt")) as f:
    requirements = f.read().splitlines()

with open(path.join(here, pkg_name, "version.py")) as f:
    exec(f.read())

setup(
    name="workflow-array-ephys",
    python_requires=">=3.7",
    version=__version__,  # noqa: F821
    description="Extracellular electrophysiology pipeline using the DataJoint elements",
    long_description=long_description,
    author="DataJoint",
    author_email="info@datajoint.com",
    license="MIT",
    url="https://github.com/datajoint/workflow-array-ephys",
    keywords="neuroscience datajoint ephys",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=requirements,
)
