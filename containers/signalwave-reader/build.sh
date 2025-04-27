#!/bin/bash

docker build --no-cache -t harbor.home.virtualelephant.com/ve-lab/influx-reader:latest .
docker push harbor.home.virtualelephant.com/ve-lab/influx-reader:latest