#!/bin/bash

set -e

cd ${GITHUB_WORKSPACE}/"${DOCKER_CONTEXT_DIR}"

# Use static tag name for the app image
DOCKER_IMAGE_TAG=enclave

##########################
# Build app docker image #
##########################
docker build \
    -f "${DOCKERFILE_PATH}" \
    -t "${DOCKER_IMAGE_TAG}:latest" \
    .

#############
# Build EIF #
#############
cd ${GITHUB_WORKSPACE}/.github/workflows/scripts

# Create directory for EIF output
if [[ ! -d ${EIF_OUTPUT_PATH} ]]; then
    mkdir ${EIF_OUTPUT_PATH}
fi

# Build EIF builder image
docker build -t eif-builder -f eif-builder.Dockerfile .

# Get local docker socket path
DOCKER_SOCK_PATH=$(docker context inspect | jq -r '.[0].Endpoints.docker.Host' | sed "s^unix://^^")

# Run EIF builder with Docker-in-Docker
docker run -v ${DOCKER_SOCK_PATH}:/var/run/docker.sock -v ${EIF_OUTPUT_PATH}:/output -e DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG} eif-builder

# Output
echo "eif-file-path=${EIF_OUTPUT_PATH}/enclave.eif" >> ${GITHUB_OUTPUT}
echo "eif-info-path=${EIF_OUTPUT_PATH}/eif-info.txt" >> ${GITHUB_OUTPUT}
