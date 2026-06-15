data "archive_file" "get_menu" {
  type        = "zip"
  source_dir  = "${path.root}/../src/lambdas/get-menu"
  output_path = "${path.root}/../tmp/get-menu.zip"
}

resource "aws_iam_role" "get_menu" {
  name = "${local.project_name}-get-menu"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "get_menu_basic" {
  role       = aws_iam_role.get_menu.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "get_menu" {
  function_name    = "${local.project_name}-get-menu"
  filename         = data.archive_file.get_menu.output_path
  source_code_hash = data.archive_file.get_menu.output_base64sha256
  handler          = "index.handler"
  runtime          = "nodejs22.x"
  memory_size      = 512
  role             = aws_iam_role.get_menu.arn
}

