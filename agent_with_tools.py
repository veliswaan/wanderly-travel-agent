# ============================================================
# Phase 1b: Agent with Tools (Building on simple_agent.py)
# ============================================================
# pip install strands-agents strands-agents-tools
#
# This extends our simple Wanderly agent by adding TOOLS.
# Tools let the agent take actions and fetch real data.

from strands import Agent, tool
from strands.models import BedrockModel

# ============================================================
# TOOLS: Functions the agent can call autonomously
# ============================================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In production, this would call a real weather API
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
    # Daily costs in USD
    budgets = {
        "Nairobi": {"budget": 50, "mid-range": 120, "luxury": 300},
        "Mombasa": {"budget": 40, "mid-range": 100, "luxury": 250},
    }
    city_budget = budgets.get(city, {"budget": 45, "mid-range": 110, "luxury": 275})
    daily = city_budget.get(style, 110)
    total = daily * days
    return f"Estimated {style} budget for {days} days in {city}: ${total} (${daily}/day)"


# ============================================================
# AGENT: Same Wanderly personality, now with superpowers!
# ============================================================

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

agent = Agent(
    model=model,
    system_prompt="""You are Wanderly, a friendly travel assistant. Help users plan trips, 
find local gems, and navigate destinations. Be practical, culturally aware, and concise. 
Never make bookings or guarantee prices—recommend verifying with official sources.

Use your tools to provide accurate, real-time information when available.""",
    tools=[get_weather, search_attractions, estimate_budget]
)

# ============================================================
# The agent AUTONOMOUSLY decides which tools to call!
# ============================================================

response = agent("I'm planning 3 days in Nairobi on a mid-range budget. What's the weather like and what should I see?")
print(response)
