#!/bin/bash

# Update package lists
sudo apt-get update

# Install prerequisites
sudo apt-get install -y software-properties-common

# Add deadsnakes PPA repository for Python 3.11
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

# Install Python 3.11 and related packages
sudo apt-get install -y python3.11 python3.11-distutils python3.11-venv

# Install pip for Python 3.11
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.11 get-pip.py
rm get-pip.py

# Upgrade pip to the latest version
pip install --upgrade pip

# Install Git LFS
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install -y git-lfs
git lfs install

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

