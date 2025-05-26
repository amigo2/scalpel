
# 1) Create the bucket (ACLs default to private)
resource "aws_s3_bucket" "spa_bucket" {
  bucket = "scalpel-frontend-bucket"   # ← change to your globally unique name

  tags = {
    Name        = "Scalpel-SPA"
    Environment = "prod"
  }
}

# 2) Enforce bucket-owner object ownership (disables all ACLs)
resource "aws_s3_bucket_ownership_controls" "disable_acls" {
  bucket = aws_s3_bucket.spa_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# 3) Block public ACLs but allow policies
resource "aws_s3_bucket_public_access_block" "spa_public_block" {
  bucket                  = aws_s3_bucket.spa_bucket.id
  block_public_acls       = true    # ignore any ACL grants
  ignore_public_acls      = true
  block_public_policy     = false   # allow policies
  restrict_public_buckets = false
}

# 4) Grant public-read via a bucket policy
data "aws_iam_policy_document" "spa_public_read" {
  statement {
    sid    = "AllowPublicReadGetObject"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.spa_bucket.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "spa_public_read" {
  bucket = aws_s3_bucket.spa_bucket.id
  policy = data.aws_iam_policy_document.spa_public_read.json
}

# 5) Configure static-site hosting
resource "aws_s3_bucket_website_configuration" "spa_website" {
  bucket = aws_s3_bucket.spa_bucket.id

  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "index.html"
  }
}
