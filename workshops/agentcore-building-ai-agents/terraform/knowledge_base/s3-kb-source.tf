# --- A source knowledge bucket with org documents
resource "aws_s3_bucket" "kb_source" {
    bucket        = "${var.project_name}-kb-source"
    force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "kb_spirce" {
    bucket = aws_s3_bucket.kb_source.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

# --- Upload knowledge base documents (after KB resources was created)
locals {
    kb_documents = toset([
        "troubleshooting-guide.txt",
        "laptop-maintenance-guide.txt",
        "smartphone-setup-guide.txt",
        "monitor-calibration-guide.txt",
        "wireless-connectivity-guide.txt",
        "warranty-service-guide.txt",
    ])
}

resource "aws_s3_object" "kb_docs" {
    for_each     = local.kb_documents
    bucket       = aws_s3_bucket.kb_source.id
    key          = each.value
    source       = "${path.root}/../knowledge-base/${each.value}"
    content_type = "text/plain"
    etag         = filemd5("${path.root}/../knowledge-base/${each.value}")
    depends_on = [ aws_s3_bucket.kb_source ]
}

# For triggering sync when docs change
locals {
  kb_source_docs_hash = sha256(join(",", [for f in sort(tolist(local.kb_documents)) : filemd5("${path.root}/../knowledge-base/${f}")]))
}