#!/usr/bin/env bash

# This script is used to create a temporary
# 2GB swapfile in the Orange Pi SBC since
# compiling dependencies require a lot of
# memory.

sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon --show
free -m
