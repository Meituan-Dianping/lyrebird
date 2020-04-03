#!/bin/bash
is_connect=0
for ((i=1;i<20;i++))
do
  echo "第 $i 次尝试连接 lyrebird"
  code=`curl -o /dev/null --retry 3 --retry-max-time 8 -s -w %{http_code} 127.0.0.1:9090/api/status`
  echo "lyrebird 状态码： $code"
  base=200
  if [[ $code -eq $base ]];then
    echo "lyrebird connected !"
    is_connect=1
    break
  fi
  sleep 3
done
echo $is_connect
if [[ $is_connect -eq 0 ]];then
  ps -ef|grep serve.py | grep -v grep|awk '{printf $2}'|xargs kill -9
  ps -ef|grep lyrebird | grep -v grep|awk '{printf $2}'|xargs kill -9
  echo "lyrebird unconneted"
  exit 8
fi
echo "last"
