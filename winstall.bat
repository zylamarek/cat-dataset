@echo off
PATH = %PATH%;%USERPROFILE%\Miniconda3\Scripts
conda create -n cat-dataset pip python=3.6 -y
call activate cat-dataset
pip install -r requirements.txt
