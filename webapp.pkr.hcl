variable "artifact_path" {
  type    = string
  default = "app.zip"
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
  region        = "us-east-1"
  #   source_ami_filter {
  #     filters = {
  #       name                = "ubuntu/images/*ubuntu-jammy-24.04-amd64-server-*/"
  #       root-device-type    = "ebs"
  #       virtualization-type = "hvm"
  #     }
  #     most_recent = true
  #     owners      = ["194722440631"]
  #   }
  source_ami   = "ami-0866a3c8686eaeeba"
  ssh_username = "ubuntu"
  vpc_id       = "vpc-0a4ad9ede797539a9"
  subnet_id    = "subnet-002af89dae1d04a65"
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {

    environment_vars = [
      "MYSQL_USER=root",
      "MYSQL_PASSWORD=password123",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306",
      "MYSQL_DATABASE=csye6225",
      "TEST_MYSQL_DATABASE=test_db",
    ]

    inline = [
      "sudo useradd -m -s /usr/sbin/nologin csye6225",
      "sudo mkdir -p /opt/csye6225/app",
      "sudo chown csye6225:csye6225 /opt/csye6225/app"
    ]
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

    environment_vars = [
      "MYSQL_USER=root",
      "MYSQL_PASSWORD=password123",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306",
      "MYSQL_DATABASE=csye6225",
      "TEST_MYSQL_DATABASE=test_db",
    ]

    inline = [
      "sudo chown -R csye6225:csye6225 /opt/csye6225/app",
      "sudo apt-get update",
      "sudo apt-get install -y python3 python3-pip",
      "sudo -u csye6225 unzip /tmp/app.zip -d /opt/csye6225/app",
      "sudo -u csye6225 pip3 install -r /opt/csye6225/app/requirements.txt",
      "sudo mv /tmp/app.service /etc/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable csye6225"
    ]
  }
}