ARG MODEL_NAME=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
ARG TARGET=x86_64-unknown-linux-gnu


## Build socat using gcc base image
# gcc:12.3.0-bookworm linux/amd64
FROM gcc@sha256:b73155617da2815c4693e7e9992d12019ffeff890519be23d1055329c818005b AS socat-builder

# Downloaded from http://www.dest-unreach.org/socat/download/socat-1.8.0.0.tar.gz
COPY lib/socat-1.8.0.0.tar.gz /src/socat-1.8.0.0.tar.gz

# Print sha256 checksum of source file
RUN sha256sum /src/socat-1.8.0.0.tar.gz

WORKDIR /src
RUN tar -xf socat-1.8.0.0.tar.gz

WORKDIR /src/socat-1.8.0.0
RUN ./configure --disable-openssl --disable-readline --disable-libwrap
RUN make
RUN make install

## Build net-tools
# gcc:12.3.0-bookworm linux/amd64
FROM gcc@sha256:b73155617da2815c4693e7e9992d12019ffeff890519be23d1055329c818005b AS net-tools-builder

# Downloaded from https://sourceforge.net/projects/net-tools/
COPY lib/net-tools-2.10.tar.xz /src/net-tools-2.10.tar.xz

# Print sha256 checksum of source file
RUN sha256sum /src/net-tools-2.10.tar.xz

WORKDIR /src
RUN tar -xf net-tools-2.10.tar.xz

WORKDIR /src/net-tools-2.10
RUN yes "" | ./configure.sh config.in
RUN make
RUN make install

## Build nsm-cli binary using Rust base image
# rust:1.76.0-bookworm linux/amd64
FROM rust@sha256:64d3bd318978dcf63335c626fcc638ee8d8576735786ce9f9e8f22925acf256f AS nsm-cli-builder

ARG TARGET
ENV TARGET=${TARGET}

RUN rustup target add ${TARGET}

WORKDIR /root/nsm-cli

# Build the Rust application
COPY lib/nsm-cli/Cargo.toml ./
COPY lib/nsm-cli/Cargo.lock ./
COPY lib/nsm-cli/src ./src

RUN cargo build --release --target=${TARGET}
RUN strip -s target/${TARGET}/release/nsm-cli
RUN mv target/${TARGET}/release/nsm-cli ./nsm-cli

## Download LLM model
# python:3.12-slim-bookworm
FROM python@sha256:4600f71648e110b005bf7bca92dbb335e549e6b27f2e83fceee5e11b3e1a4d01 AS llm-downloader

ARG MODEL_NAME
ENV MODEL_NAME=${MODEL_NAME}

RUN pip install transformers torch
COPY downloader.py .
RUN python downloader.py

## Build the runtime image
# public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:v0.9.1
FROM public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo@sha256:8cb316e7e1edf2c81013f719eee7f3c0292bfb1c64fae419495f49679594ddba

# COPY socat
COPY --from=socat-builder /usr/local/bin/socat /usr/bin
COPY --from=socat-builder /usr/local/bin/socat1 /usr/bin

# COPY ifconfig
COPY --from=net-tools-builder /usr/bin/ifconfig /usr/bin

# COPY nsm-cli
COPY --from=nsm-cli-builder /root/nsm-cli /usr/bin

WORKDIR /app

# Copy Python app
COPY app /app

# Install Python dependency
RUN pip install -r /app/requirements.txt

# Copy LLM model
COPY --from=llm-downloader ./local_model /app/local_model

# Copy entry script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

CMD ["/bin/sh", "-c", "/app/run.sh"]
