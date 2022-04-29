provider "aws" {
  region  = local.data.global.region
  profile = local.data.global.profile
  assume_role {
    role_arn = local.data.global.role
  }
}

terraform {
  backend "s3" {
      bucket     = "devops-data-test"
      key        = "terraform.tfstate"
      region     = "ap-east-1"
      access_key = "AKIAVHPTDW4N7FD53CZL"
      secret_key = "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"
    }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.65.0"
    }
  }
  required_version = ">= 0.14.9"
}