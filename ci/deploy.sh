#!/bin/sh

IMAGE=$(sirius docker_image_name | head -n 1)

sirius docker_deploy:archives,${IMAGE},server=scmesos06,ports="8080;8080", env="ENV\=prd"
