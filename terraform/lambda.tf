# IAM Role for Lambda
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect    = "Allow"
    actions   = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "scalpel-lambda-exec-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "ecr_pull" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Security Group for Lambda
resource "aws_security_group" "lambda" {
  name        = "scalpel-lambda-sg"
  description = "Security group for Lambda to access Aurora"
  vpc_id      = aws_vpc.scalpel.id


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Lambda function (container image)
resource "aws_lambda_function" "scalpel" {
  function_name = "scalpel-backend"
  package_type  = "Image"
  image_uri = "${aws_ecr_repository.scalpel.repository_url}:latest"
  role          = aws_iam_role.lambda_exec.arn
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id

    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DATABASE_URL = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_rds_cluster.aurora.endpoint}:${var.db_port}/${var.db_name}"
      DEBUG        = "false"
    }
  }
}

output "lambda_arn" {
  value       = aws_lambda_function.scalpel.arn
  description = "ARN of the Lambda function"
}
