resource "aws_s3_bucket" "agent_bucket" {
  bucket = "${local.project_name}-agent-bucket"
  force_destroy = true
}

resource "aws_s3_object" "agent_zip" {
  bucket = aws_s3_bucket.agent_bucket.bucket
  key    = "agent.zip"
  source = "${path.root}/../tmp/agent_package/agent.zip"
  etag   = filemd5("${path.root}/../tmp/agent_package/agent.zip")
}

