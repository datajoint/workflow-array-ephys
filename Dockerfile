FROM datajoint/djlab:py3.8-debian

USER root
RUN apt-get update -y
RUN apt-get install git -y

USER anaconda
WORKDIR /main/workflow-array-ephys

USER root

RUN apt update -y

# Install pip
RUN apt install python3-pip -y

# Set environment variable for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install git
RUN apt-get install git -y

RUN git clone https://github.com/datajoint/workflow-array-ephys.git .

RUN pip install .
RUN pip install -r requirements_test.txt
