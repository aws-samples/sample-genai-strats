# Module 1: Creating a simple Customer Support agent Prototype

In this first module, you'll build a locally running prototype of a Customer Support Agent. Throughout this workshop, you'll evolve this prototype into a production-ready system running on Amazon Bedrock AgentCore, serving multiple customers with persistent memory, knowledge base, shared tools, and full OTEL-based observability.

But let's start simple. At first your agent will run locally, use Bedrock-provided Claude model for reasoning, and have the following tools available:

- `get_return_policy()` - Get return policy for specific products
- `get_product_info()` - Get product information

![](./images/m01-arch.png)

## Creating agent tools with Strands Agents SDK

Let's start with creating two in-process tools. "In-process" mean that the tools are running within the same process as the agent itself. Later in the workshop you'll also define remote tools the agent will access via the MCP protocol. 

Defining in-process tools in agentic frameworks like Strands SDK or LangGraph is simple — add a `@tool` decorator to a Python method and provide a description in the docstring. Strands SDK uses the function documentation, types, and arguments to provide context on the tool to your agent. Let's see this in action. 

## Step 1: Understanding the System Prompt

Explore `./src/agent/system_prompt.py`. The system prompt defines the mission of your agent - it's personality, behavior, guardrails:

```python
SYSTEM_PROMPT = """
You are a helpful and professional customer support assistant for an electronics e-commerce company.

Your role is to:
- Provide accurate information using the tools available to you
- Support the customer with technical information and product specifications, and maintenance questions
- Be friendly, patient, and understanding with customers
- Always offer additional help after answering questions
- If you can't help with something, direct customers to the appropriate contact

...REDACTED...
"""
```

## Step 2: Understanding the `get_return_policy` tool

Tool Purpose: Helps customers understand return policies for different product categories. Provides information about return windows, conditions, processes, and refund timelines. 

```python
from strands.tools import tool

@tool # <-- Turns a Python function into agentic tool
def get_return_policy(product_category: str) -> str:
    """
    Get return policy information for a specific product category.

    Args:
        product_category: Electronics category (e.g., 'smartphones', 'laptops', 'accessories')

    Returns:
        Formatted return policy details including timeframes and conditions
    """

    return_policies = {
        "smartphones": {
            "window": "30 days",
            "condition": "Original packaging, no physical damage, factory reset required",
            "process": "Online RMA portal or technical support",
            "refund_time": "5-7 business days after inspection",
            "shipping": "Free return shipping, prepaid label provided",
            "warranty": "1-year manufacturer warranty included",
        },
        ...REDACTED...
    }
```

Explore the full file at `src/agent/tools/return_policy.py`. 

## Step 3: Understanding the `get_product_info` tool

Tool purpose: Provides customers with product specs, warranties, features, and compatibility information to help them make informed decisions.

```python
from strands.tools import tool

@tool # <-- Turns a Python function into agentic tool
def get_product_info(product_type: str) -> str:
    """
    Get detailed technical specifications and information for electronics products.

    Args:
        product_type: Electronics product type (e.g., 'laptops', 'smartphones', 'headphones', 'monitors')
    Returns:
        Formatted product information including warranty, features, and policies
    """
    products = {
        "laptops": {
            "warranty": "1-year manufacturer warranty + optional extended coverage",
            "specs": "Intel/AMD processors, 8-32GB RAM, SSD storage, various display sizes",
            "features": "Backlit keyboards, USB-C/Thunderbolt, Wi-Fi 6, Bluetooth 5.0",
            "compatibility": "Windows 11, macOS, Linux support varies by model",
            "support": "Technical support and driver updates included",
        },
        ...REDACTED...
    }
```
Explore the full file: `src/agent/tools/product_info.py`

## Step 4: Understanding the Customer Support Agent

Now that you understand how to create in-process tools, let's see how to create an agent, attach it to these tools, and run it locally.

Explore `src/agent/agent.py`. You can see that it uses Anthropic Claude Sonnet 4.6 model via Bedrock. The agent is initialized with a system prompt and has the two tools you explored earlier attached:

```python
# See system_prompt.py for System Prompt
from system_prompt import SYSTEM_PROMPT

# Define the model
model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

# The list of tools
tools = [
    get_product_info,
    get_return_policy,
    get_technical_support, # Doesn't do anything yet, you will configure this tool in later module
    mcp_tools_list         # Doesn't do anything yet, you will configure this tool in later module
]

# Defining the agent (inside of the invoke() method)
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=tools,
    session_manager=session_manager, # Doesn't do anything yet, you will configure this in later module
    callback_handler=None,
)
```

## Step 5: Running locally vs in cloud

The same `agent.py` file will run both on your local machine and in AWS on AgentCore Runtime (you'll deploy it in Module 5). At the bottom of `agent.py` you can see a code snippet that identifies the environment using the `AGENTCORE_RUNTIME_URL` variable, which is always available when running on AgentCore:

```python
if __name__ == "__main__":
    if os.environ.get("AGENTCORE_RUNTIME_URL"):
        print("Initializing OTEL...") # Initializes OpenTelemetry 
        opentelemetry.instrumentation.auto_instrumentation.initialize()

        print("Running on AgentCore, starting server...")
        app.run()          # starts the AgentCore HTTP server
    else:
        print("Running locally...")
        asyncio.run(run_locally_async()) # starts an interactive prompt loop
```

When running locally, `run_locally_async()` starts an interactive prompt loop right in the Terminal, so you can type questions and see responses without editing any code.

## Step 6: Testing the agent locally

Start the agent:

```bash
make run-agent-locally
```

> You can ignore warnings about MEMORY_ID and mcp_client. You'll add these components in upcoming modules.

You'll see an interactive prompt:

```
--------------------
Welcome to the AwesomeCorp Customer Support Agent

--------------------
User prompt (type 'exit' to quit):
```

#### Test general capabilities

Ask the agent:

```text
How can you help me?
```

The agent describes its capabilities as defined in the system prompt:

```
Hi there! Welcome to our customer support! I'm here to help you with a range of questions and concerns related to our electronics products. Here's what I can assist you with:

1. Product Information - Get detailed specs, features, ...REDACTED...
2. Return & Warranty Policies - Find out about return timeframes, ...REDACTED...
3. Technical Support - Help with troubleshooting issues, setup guides, ...REDACTED...

Just let me know what you need help with, and I'll do my best to assist you! What can I do for you today?
```

> Keep in mind, LLMs are non-deterministic. The response you receive is expected to differ from examples shown in this workshop.

As expected, the agent is behaving according to what is defined in the system prompt. In the following modules you'll also add tools, knowledge base, and memory to make your agent more helpful. 

#### Test the `get_product_info` tool

Ask the agent:

```text
What do you know about headphones?
```

The agent automatically invokes `get_product_info` based on the prompt:

```text
I'd be happy to help you learn about headphones! Let me pull up our detailed product information for you.

[Tool called: get_product_info]

### Headphones Information

Here's what I know about our headphones:

Warranty:
• 1-year manufacturer warranty

Specifications:
• Available in wired and wireless options  
• Frequency range: 20Hz-20kHz  
• Noise cancellation technology
...REDACTED...
```

#### Test the `get_return_policy` tool

Ask the agent: 

```text
My headphones are broken, can I return them?
```

The agent automatically invokes `get_return_policy` based on the prompt:

```text
I'll get the return policy information for headphones for you.

[Tool called: get_return_policy]

According to our return policy for headphones:

Headphones Return Policy:
- Return window: 30 days from delivery
- Condition: Must be in original condition with all included components
- Process: Contact technical support to initiate the return process
- Refund timeline: 5-7 business days after inspection
- Shipping: Return shipping policies vary depending on your location
- Warranty: Standard manufacturer warranty still applies during this period
...REDACTED...
```

Type `exit` to quit. The agentic loop is working! The agent is picking the right tools automatically!

## Congratulations!

You've just learned to create a real AI Agent using Strands Agents SDK and Amazon Bedrock!

- Built an agent with 2 custom local tools (`get_return_policy`, `get_product_info`)
- Tested the agentic loop — the agent selects tools automatically based on context
- Established the foundation for the upcoming modules

Current limitations you'll address in next steps:

- No knowledge base integration — knowledge is hardcoded into the tools
- No memory — the agent doesn't remember past conversations
- Tools are embedded in the app — not reusable across agents
- Running locally only — not scalable
- No authentication, authorization, or access controls
- Minimal observability — debugging is done locally
- No access to enterprise APIs or customer data

## Next step

Proceed to [Module 2](m02-knowledge-base.md) to integrate your agent with a Knowledge Base.
