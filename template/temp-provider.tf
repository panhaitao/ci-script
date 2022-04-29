provider "aws" {
  region  = local.data.global.region
  profile = local.data.global.profile
  assume_role {
    role_arn = local.data.global.role
  }
  shared_config_files = [".aws/conf"]
  shared_credentials_files = [".aws/credential"]
}

terraform {
  backend "s3" {
      bucket     = "{{ vars.s3.bucket }}"
      key        = "{{ vars.s3.key }}"
      region     = "{{ vars.s3.region }}"
      access_key = "{{ vars.s3.ak }}"
      secret_key = "{{ vars.s3.sk }}"
    }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.5"
    }
  }
  required_version = ">= 0.14.9"
}
