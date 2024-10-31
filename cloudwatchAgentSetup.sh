#!/bin/bash

# Install CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create CloudWatch agent configuration file with static log stream name
cat <<EOT > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
    "metrics": {
        "namespace": "CSYE6225/webapp_metrics",
        "metrics_collected": {
        "statsd": {
            "service_address": ":8125",
            "metrics_collection_interval": 10,
            "metrics_aggregation_interval": 10
        }
        }
    },
    "logs": {
        "logs_collected": {
        "files": {
            "collect_list": [
            {
                "file_path": "/var/log/syslog",
                "log_group_name": "/aws/ec2/csye6225-webapp-syslog",
                "log_stream_name": "csye6225-webapp-log-stream-syslog",
                "timezone": "UTC"
            },
            {
                "file_path": "/var/log/cloud-init.log",  
                "log_group_name": "/aws/ec2/csye6225-webapp-cloud-init",  
                "log_stream_name": "csye6225-webapp-log-stream-cloud-init",
                "timezone": "UTC"
            }
            ]
        }
        },
        "force_flush_interval": 5
    }
}
EOT

# Start CloudWatch Agent with the new config
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
