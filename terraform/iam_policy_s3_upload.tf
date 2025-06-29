resource "aws_iam_policy" "lambda_s3_upload" {
  name        = "scalpel-lambda-s3-upload"
  description = "Allow Lambda to upload files to S3 /uploads/ path"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject"
        ],
        Resource = "arn:aws:s3:::scalpel-frontend-bucket/uploads/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_upload_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_s3_upload.arn
}


