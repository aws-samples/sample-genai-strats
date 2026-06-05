resource "aws_s3vectors_vector_bucket" "kb_vectors" {
    vector_bucket_name = "${var.project_name}-kb-vectors"
    force_destroy      = true
}

resource "aws_s3vectors_index" "kb_vectors" {
    vector_bucket_name = aws_s3vectors_vector_bucket.kb_vectors.vector_bucket_name
    index_name         = "bedrock-knowledge-base-index"
    data_type          = "float32"
    dimension          = 1024
    distance_metric    = "cosine"

    metadata_configuration {
        non_filterable_metadata_keys = ["AMAZON_BEDROCK_TEXT_CHUNK"]
    }
}
