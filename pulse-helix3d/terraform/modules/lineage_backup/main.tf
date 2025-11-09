variable "bucket_name" {
  type = string
}

resource "aws_s3_bucket" "lineage" {
  bucket = var.bucket_name
  versioning {
    enabled = true
  }
  lifecycle_rule {
    id      = "expire"
    enabled = true
    expiration {
      days = 90
    }
  }
}
