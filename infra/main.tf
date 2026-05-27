# infra/main.tf
provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

# S3 Bucket for Feast Offline Store and Model Artifact Registry
resource "aws_s3_bucket" "mlops_bucket" {
  bucket        = "ntq-29-mlops-bucket"
  force_destroy = true # Allows clean tear-down for portfolio purposes
}

resource "aws_s3_bucket_versioning" "mlops_bucket_versioning" {
  bucket = aws_s3_bucket.mlops_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Outputs so our Kubernetes cluster knows where to point
output "s3_bucket_name" {
  value       = aws_s3_bucket.mlops_bucket.id
  description = "The S3 bucket serving as our Feast offline feature store."
}
