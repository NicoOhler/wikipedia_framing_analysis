#!/bin/bash

# Create and activate conda environment
conda create -y -c conda-forge -n framing_analysis python=3.10.12 matplotlib
source $(conda info --base)/etc/profile.d/conda.sh # initialize conda in bash
conda activate framing_analysis

# Install packages
yes | pip install framefinder
conda install -y -c conda-forge sentence-transformers
conda install -y nltk
    #conda install -y conda-forge::tqdm
conda install -y anaconda::requests
#yes | pip install deep-translator
#conda install -y conda-forge::wikipedia-api

# Run Python script
python script.py

# Remove conda environment
# conda deactivate
# conda remove -y -n framing_analysis --all                          
