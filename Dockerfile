FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo \
    python \
    python3.7 \
    python3-pip \
    git \
    libsdl2-dev \
    libfreetype6-dev \
    libsdl2-mixer-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libjpeg-dev \
    libpng-dev \
    libportmidi-dev \
    && \
    pip3 install virtualenv

RUN groupadd -g 998 wheel
RUN useradd -u 1000 -mg users -G wheel dev -s /bin/bash
RUN echo '%wheel ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
