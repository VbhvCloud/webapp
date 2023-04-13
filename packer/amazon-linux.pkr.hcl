packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "ami_users" {
  type = list(string)
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "source_ami" {
  type    = string
  default = "ami-0dfcb1ef8550277af"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "ssh_username" {
  type    = string
  default = "ec2-user"
}

variable "subnet_id" {
  type    = string
  default = "subnet-096d56e8c34dd55e7"
}

variable "vpc_id" {
  type    = string
  default = "vpc-0a4dc05ee10ccc4d1"
}

variable "ami_name" {
  type    = string
  default = "webapp-ami"
}
variable "environment" {
  type    = string
  default = "dev"
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "amazon-ebs" "webapp-ami" {
  profile       = "dev"
  ami_name      = "${var.ami_name}-${local.timestamp}"
  ami_users     = "${var.ami_users}"
  instance_type = "${var.instance_type}"
  region        = "${var.region}"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"
  subnet_id     = "${var.subnet_id}"
  tags = {
    Name        = "${var.ami_name}-${local.timestamp}"
    Environment = "${var.environment}"
  }
  vpc_id = "${var.vpc_id}"

  launch_block_device_mappings {
    device_name           = "/dev/xvda"
    delete_on_termination = true
  }
}

build {
  sources = [
    "source.amazon-ebs.webapp-ami"
  ]

  provisioner "file" {
    source      = "../webapp"
    destination = "/home/ec2-user/webapp"
  }

  provisioner "shell" {
    script = "packer/provision.sh"
  }
}
