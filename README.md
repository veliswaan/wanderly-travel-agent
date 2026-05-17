# Wanderly: AI Travel Assistant with Strands Agents

A progressive demo showing how to build, enhance, and deploy an AI travel assistant using [Strands Agents](https://strandsagents.com/) and [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/).

Built for **AgentCon 2026 Kenya** 🇰🇪

## What You'll Learn

This repo demonstrates the journey from a simple chatbot to a production-deployed AI agent:

| File | What It Shows |
|------|---------------|
| `simple_agent.py` | Minimal agent in ~10 lines of code |
| `agent_with_tools.py` | Adding tools for real-world capabilities |
| `agentcore_integration.py` | Deploying to AWS for production use |

## Quick Start

### Prerequisites
- Python 3.10+
- AWS account with Bedrock access
- AWS CLI configured

### Installation
```bash
pip install strands-agents bedrock-agentcore bedrock-agentcore-starter-toolkit
```

### Run Locally
```bash
# Simple agent
python simple_agent.py

# Agent with tools
python agent_with_tools.py
```

### Deploy to AWS
```bash
# Configure
agentcore configure --entrypoint agentcore_integration.py --name wanderly_travel_agent --disable-memory --non-interactive

# Deploy
agentcore deploy

# Test
agentcore invoke '{"prompt": "Plan my trip to Nairobi!"}'
```

## The Agent: Wanderly

Wanderly is a friendly travel assistant that helps users:
- Get weather information for destinations
- Discover attractions by category (wildlife, culture, food)
- Estimate travel budgets

### Tools Available
- `get_weather(city)` - Current weather conditions
- `search_attractions(city, category)` - Tourist attractions
- `estimate_budget(city, days, style)` - Trip cost estimation

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  simple_agent   │ --> │ agent_with_tools│ --> │   agentcore     │
│                 │     │                 │     │   integration   │
│  Basic chat     │     │  + Weather      │     │  + AWS Deploy   │
│  Claude Sonnet  │     │  + Attractions  │     │  + Production   │
│                 │     │  + Budget       │     │    ready        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Production Integration

Once deployed, integrate your agent into any application:

### Python
```python
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:runtime/wanderly_travel_agent',
    runtimeSessionId='unique-session-id-minimum-33-characters',
    payload=json.dumps({"prompt": "Plan my trip to Nairobi!"})
)

result = json.loads(response['response'].read())
print(result)
```

### JavaScript
```javascript
const { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } = require('@aws-sdk/client-bedrock-agentcore');

const client = new BedrockAgentCoreClient({ region: 'us-east-1' });
const response = await client.send(new InvokeAgentRuntimeCommand({
    agentRuntimeArn: 'arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:runtime/wanderly_travel_agent',
    runtimeSessionId: 'unique-session-id-minimum-33-characters',
    payload: JSON.stringify({ prompt: 'Plan my trip to Nairobi!' })
}));
```

## IAM Permissions Required

For deployment, your IAM user needs:
- `AmazonEC2ContainerRegistryFullAccess`
- `AWSCodeBuildAdminAccess`
- `AmazonS3FullAccess`
- `IAMFullAccess`
- Custom policy for `bedrock-agentcore:*`

## Resources

- [Strands Agents Documentation](https://strandsagents.com/docs/)
- [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Claude on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html)

## License

MIT

---

Built with ❤️ for the developer community in Kenya
