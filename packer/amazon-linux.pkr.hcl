packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "ami_users" {
  type    = list(string)
  default = ["708350626625", "968826851366", "397760876919"]
}

variable "region" {
  type    = string
  default = "us-east-1"
}

source "amazon-ebs" "webapp-ami" {
  profile       = "dev"
  ami_name      = "webapp-ami"
  ami_users     = "${var.ami_users}"
  instance_type = "t2.micro"
  region        = "${var.region}"
  source_ami    = "ami-0dfcb1ef8550277af"
  ssh_username  = "ec2-user"
  subnet_id     = "subnet-096d56e8c34dd55e7"
  tags = {
    Name        = "webapp-ami"
    Environment = "dev"
  }
  vpc_id = "vpc-0a4dc05ee10ccc4d1"

  launch_block_device_mappings {
    device_name           = "/dev/xvda"
    delete_on_termination = "${var.region}"
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
