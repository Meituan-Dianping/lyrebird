#!/usr/bin/env bash

echo "***************************"
echo "          start            "
echo "***************************"

echo "************ create python virtual environment ***************"
python3 -m venv --clear venv

echo "************ activate virtual environment ***************"
source ./venv/bin/activate

echo "************ upgrage pip ***************"
pip install --upgrade pip

echo "************ install from requirements.txt ***************"
pip install -r requirements.txt

echo "***************************"
echo "          end              "
echo "***************************"
