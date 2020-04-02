#!/usr/bin/env bash

python3 -m venv --clear ../venv

source ../venv/bin/activate

pip install --upgrade pip

pip install -e ..[dev]

python -m pytest test_lb_req_body.py
