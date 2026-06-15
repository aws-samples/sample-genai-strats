data "archive_file" "interceptor" {
  type        = "zip"
  source_dir  = "${path.root}/../src/lambdas/interceptor"
  output_path = "${path.root}/../tmp/interceptor.zip"
}

resource "aws_iam_role" "interceptor" {
  name = "${local.project_name}-interceptor"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "interceptor_basic" {
  role       = aws_iam_role.interceptor.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "interceptor" {
  function_name    = "${local.project_name}-interceptor"
  filename         = data.archive_file.interceptor.output_path
  source_code_hash = data.archive_file.interceptor.output_base64sha256
  handler          = "index.handler"  # change to index2.handler for the mutating variant
  runtime          = "nodejs22.x"
  memory_size      = 512
  role             = aws_iam_role.interceptor.arn
}
