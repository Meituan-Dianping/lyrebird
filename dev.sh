#!/usr/bin/env bash

echo "***************************"
echo "   Lyrebird setup start   "
echo "***************************"

# 如果已经有venv目录，删除此目录
if [ -e "./venv/" ]; then
rm -rf ./venv/
fi

mkdir venv
python3 -m venv ./venv

# 有些设备上虚拟环境中没有pip，需要通过easy_install安装
if [ ! -e "./venv/bin/pip" ] ;then
echo "pip no exist, install pip with easy_install"
./venv/bin/easy_install pip
fi

source ./venv/bin/activate
pip3 install -r ./requirements.txt

# 如果没有data目录，创建此目录
if [ ! -e "./data/" ]; then
mkdir ./data
fi

echo "***************************"
echo "   Lyrebird setup finish   "
echo "***************************"
