FROM python:3.12.11 AS downloader

RUN pip install transformers torch
COPY downloader.py .
RUN python downloader.py


FROM public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:v0.9.1

ENV VLLM_USE_V1=0
RUN apt-get update && apt-get -y install net-tools socat
RUN mkdir -p /workspace
WORKDIR /workspace
RUN mkdir -p /workspace/local_model
COPY main.py /workspace/main.py
COPY --from=downloader ./local_model /workspace/local_model
COPY requirements.txt /workspace/requirements.txt
RUN pip install -r /workspace/requirements.txt
COPY run.sh /workspace/run.sh
RUN chmod +x /workspace/run.sh
ENTRYPOINT ["/bin/sh", "-c", "/workspace/run.sh"]
# ENTRYPOINT ["/bin/bash"]
