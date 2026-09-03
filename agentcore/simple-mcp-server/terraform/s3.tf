resource "aws_s3_bucket" "mcp_server" {
  bucket        = "${local.project_name}-mcp-server"
  force_destroy = true
}

locals {
  mcp_server_zip = "${path.root}/../tmp/mcp_server_package/mcp_server.zip"
}

resource "aws_s3_object" "mcp_server_package_zip" {
  bucket = aws_s3_bucket.mcp_server.bucket
  key    = "mcp_server-${filemd5(local.mcp_server_zip)}.zip"
  source = local.mcp_server_zip
  etag   = filemd5(local.mcp_server_zip)
}

