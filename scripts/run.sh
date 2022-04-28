#!/bin/bash
ROOT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; cd .. ; pwd -P )" 
export PYTHONPATH=${PYTHONPATH}:$ROOT
# rm $ROOT/parsing/output/*
python3 $ROOT/parsing/main.py
