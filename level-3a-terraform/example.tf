## Required header
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 2.70"
    }
  }
}

## Option 1: Use named profile (e.g. "academy")
provider "aws" {
  profile = "academy"
  region     = var.region
}
## OR
## Option 2: Use access key and secret access key
# provider "aws" {
#   access_key = var.access_key 
#   secret_key = var.secret_key
#   region     = var.region
# }

## Basic Resource
resource "aws_instance" "my-terraform-ec2-instance" {
  ami           = "ami-0915bcb5fa77e4892" 
  instance_type = "t2.micro"
}

## OR
## Another example, that accesses defaults from the variables.tf file
# resource "aws_instance" "my-second-terraform-ec2-instance" {
#   ami           = var.amis[var.region] 
#   instance_type = "t2.micro"
# }

