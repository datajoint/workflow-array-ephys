FROM datajoint/djlab:py3.7-debian

RUN mkdir /main/workflow-array-ephys

WORKDIR /main/workflow-array-ephys

RUN git clone https://github.com/ttngu207/workflow-array-ephys.git .

RUN pip install .
RUN pip install -r requirements_test.txt