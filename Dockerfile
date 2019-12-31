FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
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