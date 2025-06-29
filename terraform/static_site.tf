# 1) Create the bucket (ACLs default to private)
resource "aws_s3_bucket" "spa_bucket" {
  bucket = "scalpel-frontend-bucket" # must be globally unique

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
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

# 4) Static site configuration (used for local dev or S3 fallback)
resource "aws_s3_bucket_website_configuration" "spa_website" {
  bucket = aws_s3_bucket.spa_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# 5) Create CloudFront Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "spa_oai" {
  comment = "OAI for accessing SPA S3 bucket"
}

# 6) Secure bucket policy (allow CloudFront OAI to access S3)
data "aws_iam_policy_document" "spa_secure" {
  statement {
    sid    = "AllowCloudFrontAccess"
    effect = "Allow"

    principals {
      type        = "CanonicalUser"
      identifiers = [aws_cloudfront_origin_access_identity.spa_oai.s3_canonical_user_id]
    }

    actions = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.spa_bucket.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "spa_secure_policy" {
  bucket = aws_s3_bucket.spa_bucket.id
  policy = data.aws_iam_policy_document.spa_secure.json
}

# 7) CloudFront Distribution with error fallback for SPA
resource "aws_cloudfront_distribution" "spa_distribution" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "SPA frontend via CloudFront"
  default_root_object = "index.html"

  aliases = ["bistroagent.com"]

  origin {
    domain_name = aws_s3_bucket.spa_bucket.bucket_regional_domain_name
    origin_id   = "spaS3"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.spa_oai.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "spaS3"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
  }

  # 🔁 Custom error responses for SPA routing (very important)
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  viewer_certificate {
    acm_certificate_arn            = "arn:aws:acm:us-east-1:929423420164:certificate/7e067fd0-9590-4f4a-ac29-b4d253dff9ee"
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Environment = "prod"
  }
}
