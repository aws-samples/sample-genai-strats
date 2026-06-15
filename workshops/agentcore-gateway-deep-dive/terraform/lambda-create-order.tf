data "archive_file" "create_order" {
  type        = "zip"
  source_dir  = "${path.root}/../src/lambdas/create-order"
  output_path = "${path.root}/../tmp/create-order.zip"
}

resource "aws_iam_role" "create_order" {
  name = "${local.project_name}-create-order"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "create_order_basic" {
  role       = aws_iam_role.create_order.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "create_order" {
  function_name    = "${local.project_name}-create-order"
  filename         = data.archive_file.create_order.output_path
  source_code_hash = data.archive_file.create_order.output_base64sha256
  handler          = "index.handler"
  runtime          = "nodejs22.x"
  memory_size      = 512
  role             = aws_iam_role.create_order.arn
}
