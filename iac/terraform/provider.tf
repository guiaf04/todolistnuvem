terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  # Backend S3 opcional para estado remoto (desativado por padrão nesta prática autocontida)
  # backend "s3" {
  #   bucket = "<seu-bucket>"
  #   key    = "parte_04/terraform.tfstate"
  # }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.regiao
}
