# # cdn.tf

# resource "aws_cloudfront_distribution" "spa_cdn" {
#   enabled             = true
#   default_root_object = "index.html"
#   is_ipv6_enabled     = true

#   origin {
#     domain_name = aws_s3_bucket.spa_bucket.website_endpoint
#     origin_id   = "spaOrigin"
#   }

#   default_cache_behavior {
#     target_origin_id       = "spaOrigin"
#     viewer_protocol_policy = "redirect-to-https"
#     allowed_methods        = ["GET","HEAD"]
#     cached_methods         = ["GET","HEAD"]
#     forwarded_values { query_string = false }
#   }

#   custom_error_response {
#     error_code         = 404
#     response_code      = 200
#     response_page_path = "/index.html"   # SPA deep-link fallback :contentReference[oaicite:4]{index=4}
#   }

#   viewer_certificate {
#     cloudfront_default_certificate = true
#   }

#   restrictions {
#     geo_restriction { restriction_type = "none" }
#   }

#   tags = {
#     Name = "Scalpel-SPA-CDN"
#   }
# }
