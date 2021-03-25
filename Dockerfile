FROM datajoint/datajoint:py3.7-debian

WORKDIR /main

RUN git clone git+https://github.com/ttngu207/workflow-array-ephys.git
RUN pip install .
RUN pip install -r requirements_test.txt