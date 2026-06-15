# AgentCore Gateway Deep Dive - Workshop

## Overview

[Amazon Bedrock AgentCore Gateway](https://aws.amazon.com/bedrock/agentcore/) translates Lambda functions and HTTP services into [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) endpoints that any agent framework can discover and call. It handles authentication, authorization, request/response transformation, and secure outbound identity - all without changes to your tool implementations.

In this workshop, you will progressively build a collection of tools and MCP gateway for a Pizza Shop AI ordering system. You will expose pizza tools (get menu, create order, get promotions) through AgentCore Gateway and layer on increasingly sophisticated security and transformation controls.

![](./images/intro.png)

## Let's get started!

See workshop steps at [AWS Workshop Studio](https://catalog.us-east-1.prod.workshops.aws/workshops/05695036-0049-4114-a660-f15071df92dc/en-US)
