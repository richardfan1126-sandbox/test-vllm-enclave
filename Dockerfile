FROM python:3.12.11 AS downloader

RUN pip install transformers torch

COPY downloader.py .

RUN python downloader.py

FROM public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:v0.9.1

ENV VLLM_USE_V1=0

RUN pip install langchain langchain_community -q

RUN apt-get update && apt-get -y install net-tools

RUN mkdir -p /workspace

WORKDIR /workspace

RUN mkdir -p /workspace/local_model

COPY main.py /workspace/main.py

COPY --from=downloader ./local_model /workspace/local_model

ENTRYPOINT ["/bin/bash", "-c", "ifconfig lo 127.0.0.1 && /opt/venv/bin/python /workspace/main.py"]
# ENTRYPOINT ["/bin/bash"]
