#!/bin/bash

SLU4P_ROOT="$(pwd)"
echo 'export PYTHONPATH=${PYTHONPATH}:'"${SLU4P_ROOT}" >> ~/.bashrc
source ~/.bashrc