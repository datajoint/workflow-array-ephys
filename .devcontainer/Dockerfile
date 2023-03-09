FROM mcr.microsoft.com/devcontainers/python:3.9-bullseye

COPY ./requirements.txt /tmp/
RUN \
    # dev setup
    apt update && \
    apt-get install bash-completion graphviz default-mysql-client s3fs procps -y && \
    pip install --no-cache-dir --upgrade pip && \
    # workflow dependencies
    apt-get install gcc ffmpeg libsm6 libxext6 -y && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    # clean up
    rm /tmp/requirements.txt && \
    apt-get clean

ENV DJ_HOST fakeservices.datajoint.io
ENV DJ_USER root
ENV DJ_PASS simple

ENV DJ_PUBLIC_S3_MOUNT_PATH /workspaces/workflow-array-ephys/example_data
ENV RAW_ROOT_DATA_DIR /workspaces/workflow-array-ephys/example_data/raw
ENV PROCESSED_ROOT_DATA_DIR /workspaces/workflow-array-ephys/example_data/processed