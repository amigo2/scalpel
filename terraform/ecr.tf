resource "aws_ecr_repository" "scalpel" {
  name                 = "scalpel"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}
