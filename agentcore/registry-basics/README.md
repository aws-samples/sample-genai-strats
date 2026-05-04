# AgentCore Registry Basics

Demonstrates how to use the [Amazon Bedrock AgentCore Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) service via the AWS CLI.

## Overview

The `Makefile` provides targets to:

- Create and manage **registries** (logical namespaces for agent tool records)
- Create and manage **registry records** (MCP server descriptors registered in a registry)
- Submit records for approval, and approve/reject/deprecate them
- Search registry records

## Prerequisites

- AWS CLI with credentials configured

## Usage

### Registries

Commands: 
```bash
make create-registry
make list-registries
make get-registry
make delete-registry
```

Workflow:

1. Run `list-registries`. Observe empty list. 
1. Run `create-registry`. This creates a new registry. 
1. Run `get-registry`. Observe status as `CREATING`. Repeat `get-registry` until status changes to `READY`. This takes 2-3 minutes. 

### Registry Records

Commands: 

```bash
make create-mcp-record
make list-records
make get-record
make delete-record
```

Workflow:

1. Run `list-records`. Observe empty list. 
1. Run `create-mcp-record`. Observe new record ARN. 
1. Run `get-record` again. Observe status as `DRAFT`. 

### Approval Workflow

Commands: 

```bash
make submit-registry-record-for-approval
make approve-registry-record
make reject-registry-record
make deprecate-registry-record
```

Workflow:

1. Run `submit-registry-record-for-approval`. See status change to `PENDING_APPROVAL`.
1. Run `approve-registry-record`. See status change to `APPROVED`. 
1. Run `get-record`. See status as `APPROVED`. 

> Now you can search for the registry items. Items not in the `APPROVED` status will not appear in search. Repeat above steps trying to `reject` and `deprecate` registry records. 

### Search

1. Run `make search-records`. See result

## Cleanup

```bash
make delete-record
make delete-registry
```

