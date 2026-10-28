# Amazon Bedrock Fundamentals - Workshop

## Overview

[Amazon Bedrock](https://aws.amazon.com/bedrock) is a fully managed service that gives you access to foundation models from Amazon, Anthropic, Meta, Mistral AI, and other providers through a single API.

In this workshop, you work with Amazon Bedrock directly, one concept at a time: how to call a model, how to hold a conversation, how to give a model tools and knowledge, how to work with images, and how to protect your application with guardrails. Every lab is a short Python script that you run in the terminal with a single `make` command. You don't deploy any infrastructure: the labs call Amazon Bedrock APIs from your development environment.

| Section | Labs | Make targets |
|---|---|---|
| Foundational concepts | InvokeModel and Converse APIs, inference parameters, tool use, streaming, embeddings | `f1` to `f7` |
| Text patterns | Chatbot, document summarization, embeddings search, Retrieval-Augmented Generation (RAG), RAG chatbot, personalized recommendations, structured data extraction | `t1` to `t7` |
| Multimodal patterns | Image search, image understanding, multimodal chatbot | `m1` to `m3` |
| Security & safeguards | Amazon Bedrock Guardrails: console and code, invoking models with guardrails, prompt attack blocking | `s1` to `s4` |

## Let's get started!

See the workshop steps at [AWS Workshop Studio](https://catalog.us-east-1.prod.workshops.aws/workshops/05695036-0049-4114-a660-f15071df92dc/en-US), in the **[EXTRAS] Bedrock Fundamentals** section.

## Running the labs on your own

### Prerequisites

- An AWS account with credentials configured, and access to these models in `us-east-1`:
  - Anthropic Claude Sonnet 4.6 (`us.anthropic.claude-sonnet-4-6`)
  - Amazon Nova 2 Lite (`us.amazon.nova-2-lite-v1:0`)
  - Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`)
  - Amazon Titan Multimodal Embeddings (`amazon.titan-embed-image-v1`)
- [uv](https://docs.astral.sh/uv/) and `make`. uv installs Python 3.13 and the dependencies for you.

### Quick start

Run the commands from this directory:

```bash
make setup                  # install Python 3.13 and the dependencies into src/.venv
make f1                     # run the first lab
make populate-collections   # create the local vector database for labs T3 to T6
```

Each lab has a `make` target named after it, such as `make t4` or `make s3`. The Makefile also has targets for the shared setup steps: `populate-collections`, `populate-image-collection`, and `create-guardrails`.

### Project layout

```
bedrock-fundamentals/
├── Makefile                       one target per lab: make f1, make t4, make s3, ...
└── src/
    ├── 01_foundational_concepts/  labs F1 to F7
    ├── 02_text_patterns/          labs T1 to T7
    ├── 03_multimodal_image/       labs M1 to M3
    ├── 04_security_safeguards/    labs S1 to S4
    └── shared/                    datasets, sample images and documents, setup scripts
```

Files the labs generate, such as the local vector database, are stored in `tmp/`.

### Clean up

Most labs only call Amazon Bedrock APIs, and don't leave anything in your account. The Security & safeguards labs create guardrails. To delete them, and the generated files:

```bash
make delete-guardrails   # deletes the guardrails the labs created, by name
make clean               # deletes tmp/
```

Calls to Amazon Bedrock are billed at the on-demand price of each model.
