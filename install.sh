#!/bin/bash

conda create -n cat-dataset pip python=3.6 -y
source activate cat-dataset
pip install -r requirements.txt
