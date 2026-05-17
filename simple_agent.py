
# ============================================================
# Phase 1a: The Simplest Possible Agent
# ============================================================
# pip install strands-agents strands-agents-tools

from strands import Agent
from strands.models import BedrockModel

# Model selection is flexible - swap this out for any supported provider:
#   model = OpenAIModel(model_id="gpt-4o")                   # OpenAI  
#   model = AnthropicModel(model_id="claude-sonnet-4-20250514")      # Anthropic Direct
#   model = OllamaModel(model_id="llama3")                   # Local/Free

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

agent = Agent(
    model=model,
    system_prompt="""You are Wanderly, a friendly travel assistant. Help users plan trips, 
find local gems, and navigate destinations. Be practical, culturally aware, and concise. 
Never make bookings or guarantee prices—recommend verifying with official sources."""
)

response = agent("First time in Nairobi, here until Friday. What do locals recommend that tourists usually miss?")
print(response)

