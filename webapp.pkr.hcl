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
  source_ami    = "ami-0866a3c8686eaeeba"
  ssh_username  = "ubuntu"
  vpc_id        = "vpc-06fa733b7d5a8ab52"
  ssh_timeout   = "20m"
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {

    environment_vars = [
      "MYSQL_USER=ubuntu",
      "MYSQL_PASSWORD=password123",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306",
      "MYSQL_DATABASE=csye6225",
      "TEST_MYSQL_DATABASE=test_db",
    ]

    inline = [
      "sudo useradd -m -s /usr/sbin/nologin csye6225",
      "sudo mkdir -p /opt/csye6225/app",
      "sudo mkdir -p /opt/csye6225/venv/bin",
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

    expect_disconnect = true
    skip_clean        = true

    environment_vars = [
      "MYSQL_USER=ubuntu",
      "MYSQL_PASSWORD=password123",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306",
      "MYSQL_DATABASE=csye6225",
      "TEST_MYSQL_DATABASE=test_db",
    ]

    inline = [
      "sudo mkdir -p /opt/csye6225/app",
      "sudo mkdir -p /opt/csye6225/venv",
      "sudo chown -R csye6225:csye6225 /opt/csye6225",
      "sudo apt-get update",
      "sudo apt-get install -y python3-venv unzip python3 python3-pip mysql-server",
      "sudo systemctl start mysql",
      "sudo systemctl enable mysql",
      "sudo -u csye6225 python3 -m venv /opt/csye6225/venv",
      "sudo unzip /tmp/app.zip -d /opt/csye6225/app",
      "sudo chown -R csye6225:csye6225 /opt/csye6225/app",
      "sudo -u csye6225 /opt/csye6225/venv/bin/pip install -r /opt/csye6225/app/requirements.txt",
      "sudo mv /opt/csye6225/app/app.service /etc/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable app"
    ]
  }

  provisioner "shell" {

    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
    ]

    inline = [
      "sudo systemctl start mysql",
      "sudo systemctl enable mysql",
      "sudo mysql -e \"CREATE USER IF NOT EXISTS 'ubuntu'@'localhost'; ALTER USER 'ubuntu'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password123'; FLUSH PRIVILEGES;\"",
      "sudo systemctl restart mysql"
    ]
  }

  provisioner "shell" {
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
      "MYSQL_USER=ubuntu",
      "MYSQL_PASSWORD=password123",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306",
      "MYSQL_DATABASE=csye6225",
      "TEST_MYSQL_DATABASE=test_db",
    ]

    inline = [
      "sudo mysql -e \"CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;\"",
      "sudo mysql -e \"CREATE DATABASE IF NOT EXISTS $TEST_MYSQL_DATABASE;\"",
      "sudo mysql -e \"GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO 'ubuntu'@'localhost';\"",
      "sudo mysql -e \"GRANT ALL PRIVILEGES ON $TEST_MYSQL_DATABASE.* TO 'ubuntu'@'localhost';\"",
      "sudo mysql -e \"FLUSH PRIVILEGES;\""
    ]
  }
}