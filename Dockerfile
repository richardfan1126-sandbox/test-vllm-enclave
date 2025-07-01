FROM python:3.12.11 AS downloader

RUN pip install transformers torch

COPY downloader.py .

RUN python downloader.py

FROM public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:v0.9.1

ENV VLLM_USE_V1=0

RUN pip install langchain langchain_community -q

RUN mkdir -p ./local_model

COPY main.py .

COPY --from=downloader ./local_model ./local_model

ENTRYPOINT ["python", "main.py"]
