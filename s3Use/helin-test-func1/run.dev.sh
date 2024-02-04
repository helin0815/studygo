#!/bin/sh
export APP=py-robot-keyword

export RUNENV=dev
echo "dev"

# add the configuration of redis to the environment variable
export REDIS_HOST="192.168.9.73"
export REDIS_PORT=6381
export REDIS_PASSWORD="dsd-public-redis-sentinel-dev1q2w3e"
export REDIS_DB=0


python3 main.py