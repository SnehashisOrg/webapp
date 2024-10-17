variable "artifact_path" {
  type    = string
  default = "app.zip"
}

variable "demo_account_id" {
  type        = string
  description = "AWS account ID of the demo account"
  default     = "783764584160"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
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

  post-processor "manifest" {
    output     = "manifest.json"
    strip_path = true
  }

  post-processor "amazon-import" {
    keep_input_artifact = true
    license_type        = "BYOL"
    region              = var.aws_region
    s3_bucket_name      = "csye6225-dev-bkt"
    ami_name            = "webapp-shared-{{timestamp}}"
    ami_description     = "Webapp AMI shared with DEMO account"
    ami_users           = [var.demo_account_id]
  }
}