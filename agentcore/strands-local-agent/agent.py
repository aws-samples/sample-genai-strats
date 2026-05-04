from strands import Agent, tool
from strands.models import BedrockModel

@tool
def letter_counter(word: str) -> int:
    return len(word)

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0", temperature=0.3)

agent = Agent(
    system_prompt="""
    You're a helpful assistant that talks in single lymerics. And you like to return the number of letters in that lymeric.
    """,
    model=model,
    tools=[letter_counter]
)

message = "Tell me about AWS"

response = agent(message)

