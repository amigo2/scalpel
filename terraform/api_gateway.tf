resource "aws_apigatewayv2_api" "scalpel" {
  name          = "scalpel-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = [
      "http://localhost:3000",
      "https://fr18vg8hdd.execute-api.eu-west-2.amazonaws.com",
      "http://scalpel-frontend-bucket.s3-website.eu-west-2.amazonaws.com"
    ]
    allow_methods     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers     = ["*"]
    allow_credentials = true
    max_age           = 3600
  }
}


resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.scalpel.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.scalpel.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.scalpel.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.scalpel.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGWInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scalpel.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.scalpel.execution_arn}/*/*"
}


output "api_endpoint" {
  value       = aws_apigatewayv2_stage.default.invoke_url
  description = "Invoke URL for your FastAPI on Lambda"
}


