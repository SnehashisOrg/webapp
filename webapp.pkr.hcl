variable "artifact_path" {
  type    = string
  default = "app.zip"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region"
}

variable "source_ami" {
  type        = string
  default     = "ami-0866a3c8686eaeeba"
  description = "Ubuntu LTS: AMI Image ID"
}

variable "ssh_username" {
  type        = string
  default     = "ubuntu"
  description = "SSH username"
}

packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.8"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  ami_name      = "csye6225-coursework-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  instance_type = "t2.micro"
  region        = "${var.aws_region}"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"
  vpc_id        = "vpc-06fa733b7d5a8ab52"

  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = "gp2"
  }

  tags = {
    Name = "ami-csye6225-coursework-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  }
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {
    script = "updateOS.sh"
  }

  provisioner "shell" {
    script = "appDirSetup.sh"
  }

  provisioner "file" {
    source      = var.artifact_path
    destination = "/tmp/app.zip"
  }

  provisioner "file" {
    source      = "app.service"
    destination = "/tmp/app.service"
  }

  provisioner "shell" {

    expect_disconnect = true
    skip_clean        = true

    script = "appSetup.sh"
  }

  provisioner "shell" {
    script = "mysqlSetup.sh"
  }

  provisioner "shell" {
    script = "cloudwatchAgentSetup.sh"
  }

  post-processor "manifest" {
    output     = "manifest.json"
    strip_path = true
  }
}