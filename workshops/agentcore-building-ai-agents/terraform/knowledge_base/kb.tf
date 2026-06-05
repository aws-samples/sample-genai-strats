resource "aws_iam_role" "bedrock_kb" {
    name = "${var.project_name}-bedrock-kb"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Effect    = "Allow"
            Principal = { Service = "bedrock.amazonaws.com" }
            Action    = "sts:AssumeRole"
        }]
    })
}

resource "aws_iam_role_policy" "bedrock_kb" {
    name = "bedrock-kb-policy"
    role = aws_iam_role.bedrock_kb.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect   = "Allow"
                Action   = ["s3:GetObject", "s3:ListBucket"]
                Resource = [
                    aws_s3_bucket.kb_source.arn,
                    "${aws_s3_bucket.kb_source.arn}/*",
                ]
            },
            {
                Effect   = "Allow"
                Action   = ["bedrock:InvokeModel"]
                Resource = "arn:aws:bedrock:${var.region}::foundation-model/amazon.titan-embed-text-v2:0"
            },
            {
                Effect = "Allow"
                Action = [
                    "s3vectors:*"
                ]
                Resource = "*"
            },
            {
                Effect = "Allow"
                Action = [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ]
                Resource = aws_cloudwatch_log_group.kb_logs.arn
            },
        ]
    })
}

resource "aws_bedrockagent_knowledge_base" "tech_support" {
    name     = "${var.project_name}-tech-support"
    role_arn = aws_iam_role.bedrock_kb.arn

    knowledge_base_configuration {
        type = "VECTOR"
        vector_knowledge_base_configuration {
            embedding_model_arn = "arn:aws:bedrock:${var.region}::foundation-model/amazon.titan-embed-text-v2:0"
        }
    }

    storage_configuration {
        type = "S3_VECTORS"
        s3_vectors_configuration {
            index_arn = aws_s3vectors_index.kb_vectors.index_arn
        }
    }

    depends_on = [aws_iam_role_policy.bedrock_kb]
}

resource "aws_bedrockagent_data_source" "from_s3" {
    knowledge_base_id = aws_bedrockagent_knowledge_base.tech_support.id
    name              = "${var.project_name}-from-s3"

    data_source_configuration {
        type = "S3"
        s3_configuration {
            bucket_arn = aws_s3_bucket.kb_source.arn
        }
    }

    vector_ingestion_configuration {
        chunking_configuration {
            chunking_strategy = "FIXED_SIZE"
            fixed_size_chunking_configuration {
                max_tokens         = 200
                overlap_percentage = 20
            }
        }
    }
}

# --- Trigger ingestion for uploaded docs 
resource "null_resource" "kb_sync" {
    triggers = {
        # Re-run whenever any document changes or the data source is recreated
        data_source_id    = aws_bedrockagent_data_source.from_s3.id
        knowledge_base_id = aws_bedrockagent_knowledge_base.tech_support.id
        docs_hash         = local.kb_source_docs_hash
    }

    provisioner "local-exec" {
        command = <<-EOT
            aws bedrock-agent start-ingestion-job \
                --knowledge-base-id ${aws_bedrockagent_knowledge_base.tech_support.id} \
                --data-source-id ${aws_bedrockagent_data_source.from_s3.data_source_id} 
        EOT
    }

    depends_on = [aws_s3_object.kb_docs, aws_bedrockagent_knowledge_base.tech_support]
}


resource "local_file" "kb_id" {
    content  = aws_bedrockagent_knowledge_base.tech_support.id
    filename = "${path.root}/../tmp/tech_support_kb_id.txt"
}

output "kb_input_bucket_name" {
    value = aws_s3_bucket.kb_source.bucket
}

output "kb_id" {
    value = aws_bedrockagent_knowledge_base.tech_support.id
}
