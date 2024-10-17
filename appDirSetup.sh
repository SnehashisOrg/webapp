#!/bin/bash

set -e

sudo useradd -m -s /usr/sbin/nologin csye6225
sudo mkdir -p /opt/csye6225/app
sudo mkdir -p /opt/csye6225/venv/bin
sudo chown csye6225:csye6225 /opt/csye6225/app