#!/bin/sh

IMAGE=$(sirius docker_image_name | head -n 1)

sirius docker_deploy:archives,${IMAGE},server=scmesos06,ports="8080;8080;8081;8081",volumes="/opt/docs;/opt/data",env="ENV\=prd;C_FORCE_ROOT\=1"
