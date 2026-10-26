resource "aws_s3_bucket" "agent_bucket" {
  bucket        = "${var.project_name}-agent-bucket"
  force_destroy = true
}

resource "aws_s3_object" "agent_zip" {
  bucket = aws_s3_bucket.agent_bucket.bucket
  key    = "agent.zip"
  source = "${path.root}/../tmp/agent_package/agent.zip"
  # source_hash instead of etag: large files are uploaded in parts, and S3's ETag for
  # a multipart upload is not the file's MD5, so etag would show a change on every plan
  source_hash = filemd5("${path.root}/../tmp/agent_package/agent.zip")
}

