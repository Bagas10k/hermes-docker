FROM nousresearch/hermes-agent:latest

# Install additional system utilities for productivity & node tools
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ripgrep jq rsync unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Pre-seed custom skills and template data
COPY skills/ /opt/data/skills/

# Ensure workspace directory exists
RUN mkdir -p /workspace && chown -R 1000:1000 /workspace /opt/data

WORKDIR /workspace
