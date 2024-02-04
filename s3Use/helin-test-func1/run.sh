#!/bin/sh
export APP=py-robot-keyword

isExist=`env | grep ENV_PROD | wc -l`
echo $isExist
if [ $isExist -gt 0 ];then
  export RUNENV=prod
  echo "prod"
else
  export RUNENV=dev
  echo "dev"
fi
#pip3 install -r requirements.txt

# add the configuration of redis to the environment variable
export REDIS_HOST="192.168.9.73"
export REDIS_PORT=6381
export REDIS_PASSWORD="dsd-public-redis-sentinel-dev1q2w3e"
export REDIS_DB=0


python3 main.py