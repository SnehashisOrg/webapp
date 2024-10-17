#!/bin/bash

set -e

sudo mkdir -p /opt/csye6225/app

sudo mkdir -p /opt/csye6225/venv

sudo chown -R csye6225:csye6225 /opt/csye6225

sudo apt-get update

sudo apt-get install -y python3-venv unzip python3 python3-pip mysql-server

sudo systemctl start mysql

sudo systemctl enable mysql

sudo -u csye6225 python3 -m venv /opt/csye6225/venv

sudo unzip /tmp/app.zip -d /opt/csye6225/app

sudo chown -R csye6225:csye6225 /opt/csye6225/app

sudo -u csye6225 /opt/csye6225/venv/bin/pip install -r /opt/csye6225/app/requirements.txt

sudo mv /opt/csye6225/app/app.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable app