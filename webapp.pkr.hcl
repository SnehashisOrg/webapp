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
  region        = "us-east-1"
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-24.04-amd64-server-*/"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["194722440631"]
  }
  ssh_username = "ubuntu"
  vpc_id       = "vpc-0a4ad9ede797539a9"
}

build {
  name = "csye6225-coursework-ubuntu"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt-get install -y mysql-server python3 python3-pip",
      "sudo useradd -m -s /usr/sbin/nologin csye6225",
      "sudo groupadd csye6225",
      "sudo usermod -aG csye6225 csye6225"
    ]
  }

  provisioner "file" {
    source      = "app.py"
    destination = "/home/csye6225/app.py"
  }

  provisioner "file" {
    source      = "requirements.txt"
    destination = "/home/csye6225/requirements.txt"
  }

  provisioner "shell" {
    inline = [
      "sudo pip3 install -r /home/csye6225/requirements.txt",
      "sudo chown -R csye6225:csye6225 /home/csye6225",
      "sudo mv /tmp/app.service /etc/systemd/system/app.service",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable app"
    ]
  }
}