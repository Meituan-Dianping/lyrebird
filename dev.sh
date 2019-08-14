#!/usr/bin/env bash

echo "***************************"
echo "   dev setup start   "
echo "***************************"

# create python virtual environment
python3 -m venv --clear venv

# activate virtual environment
source ./venv/bin/activate

# upgrage pip
pip install --upgrade pip

# install from requirements.txt
pip3 install -r ./requirements.txt

# create data dir for debug
if [ ! -e "./data/" ]; then
mkdir ./data
fi

echo "***************************"
echo "   dev setup finish   "
echo "***************************"
