# ============================================================
# Phase 2: Deploy to AWS with Amazon Bedrock AgentCore
# ============================================================
# This takes our agent_with_tools.py and makes it cloud-ready!
#
# pip install strands-agents bedrock-agentcore

from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# ============================================================
# TOOLS: Same tools from agent_with_tools.py
# ============================================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "Nairobi": "Sunny, 24°C",
        "Mombasa": "Hot and humid, 32°C", 
        "Kisumu": "Partly cloudy, 28°C",
        "Cape Town": "Windy, 18°C",
        "Lagos": "Humid, 31°C",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@tool
def search_attractions(city: str, category: str = "all") -> str:
    """Search for tourist attractions in a city by category."""
    attractions = {
        "Nairobi": {
            "wildlife": ["Nairobi National Park", "Giraffe Centre", "David Sheldrick Elephant Orphanage"],
            "culture": ["Nairobi National Museum", "Bomas of Kenya", "Kazuri Beads"],
            "food": ["Carnivore Restaurant", "Mama Oliech", "Nyama Mama"],
        },
        "Mombasa": {
            "wildlife": ["Haller Park", "Mombasa Marine Park"],
            "culture": ["Fort Jesus", "Old Town", "Akamba Handicraft"],
            "food": ["Tamarind Restaurant", "Shehnai", "Jahazi Coffee House"],
        }
    }
    city_data = attractions.get(city, {})
    if category == "all":
        return str(city_data)
    return str(city_data.get(category, f"No {category} attractions found"))


@tool  
def estimate_budget(city: str, days: int, style: str = "mid-range") -> str:
    """Estimate daily travel budget for a city."""
    budgets = {
        "Nairobi": {"budget": 50, "mid-range": 120, "luxury": 300},
        "Mombasa": {"budget": 40, "mid-range": 100, "luxury": 250},
    }
    city_budget = budgets.get(city, {"budget": 45, "mid-range": 110, "luxury": 275})
    daily = city_budget.get(style, 110)
    total = daily * days
    return f"Estimated {style} budget for {days} days in {city}: ${total} (${daily}/day)"


# ============================================================
# AGENT: Lazy initialization to stay within timeout limits
# ============================================================

_agent = None

def get_agent():
    """Initialize agent on first request (lazy loading)."""
    global _agent
    if _agent is None:
        model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")
        _agent = Agent(
            model=model,
            system_prompt="""You are Wanderly, a friendly travel assistant. Help users plan trips, 
find local gems, and navigate destinations. Be practical, culturally aware, and concise. 
Never make bookings or guarantee prices—recommend verifying with official sources.

Use your tools to provide accurate, real-time information when available.""",
            tools=[get_weather, search_attractions, estimate_budget]
        )
    return _agent


# ============================================================
# AGENTCORE ENTRYPOINT
# ============================================================

@app.entrypoint
def invoke(payload):
    """
    AgentCore Runtime calls this function for every request.
    
    payload structure: {"prompt": "user's message here"}
    Returns: string response (must be JSON serializable)
    """
    user_message = payload.get("prompt", "Hello")
    response = get_agent()(user_message)
    return str(response)


# Required for AgentCore
if __name__ == "__main__":
    app.run()


# ============================================================
# DEPLOYMENT STEPS (using Starter Toolkit):
# ============================================================
# 1. Install the toolkit:
#    pip install bedrock-agentcore-starter-toolkit
#
# 2. Configure your agent:
#    agentcore configure --entrypoint agentcore_integration.py --name your_agent_name --disable-memory --non-interactive
#
# 3. Deploy to AWS:
#    agentcore deploy
#
# 4. Test your deployed agent:
#    agentcore invoke '{"prompt": "Plan my trip to Nairobi!"}'
# ============================================================


# ============================================================
# PRODUCTION INTEGRATION: How to call your deployed agent
# ============================================================
# 
# Once deployed, integrate your agent into any application:
#
# --- Python (Backend/API) ---
# import boto3
# import json
#
# client = boto3.client('bedrock-agentcore', region_name='us-east-1')
#
# response = client.invoke_agent_runtime(
#     agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:runtime/wanderly_travel_agent',
#     runtimeSessionId='unique-session-id-min-33-chars-here',
#     payload=json.dumps({"prompt": "Plan my trip to Nairobi!"})
# )
#
# result = json.loads(response['response'].read())
# print(result)
#
# --- JavaScript/Node.js ---
# const { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } = require('@aws-sdk/client-bedrock-agentcore');
#
# const client = new BedrockAgentCoreClient({ region: 'us-east-1' });
# const response = await client.send(new InvokeAgentRuntimeCommand({
#     agentRuntimeArn: 'arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:runtime/wanderly_travel_agent',
#     runtimeSessionId: 'unique-session-id-min-33-chars-here',
#     payload: JSON.stringify({ prompt: 'Plan my trip to Nairobi!' })
# }));
#
# --- REST API (via API Gateway) ---
# Expose your agent as a REST endpoint by connecting it to API Gateway.
# This enables integration with any frontend, mobile app, or third-party service.
#
# --- Use Cases ---
# • Web apps: Chat interface for travel planning
# • Mobile apps: In-app travel assistant
# • Slack/Discord bots: Team travel coordination
# • Voice assistants: Alexa/Google Home integration
# • Internal tools: Employee travel booking system
# ============================================================
