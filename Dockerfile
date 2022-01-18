FROM datajoint/djlab:py3.8-debian

USER root
RUN apt-get update -y
RUN apt-get install git -y

USER anaconda
WORKDIR /main/workflow-array-ephys

# Install DataJoint's remote fork of elements and workflow
RUN git clone https://github.com/datajoint/workflow-array-ephys.git .

RUN pip install .
RUN pip install -r requirements_test.txt