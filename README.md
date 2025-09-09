# 🦄 evi-run — Customizable Multi-Agent AI System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-Agents_SDK-green?style=flat-square&logo=openai&logoColor=white)](https://openai.github.io/openai-agents-python/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot_API-blue?style=flat-square&logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

[![Python CI](https://github.com/pipedude/evi-run/workflows/Python%20CI/badge.svg)](https://github.com/pipedude/evi-run/actions)
[![Docker Build](https://github.com/pipedude/evi-run/workflows/Docker%20Build%20&%20Publish/badge.svg)](https://github.com/pipedude/evi-run/actions)

**Ready-to-use customizable multi-agent AI system that combines plug-and-play simplicity with framework-level flexibility**

[🚀 Quick Start](#-quick-installation) • [🤖 Try Demo](https://t.me/my_evi_bot) • [🔧 Configuration](#-configuration) • [🎯 Features](#-features) • [💡 Use Cases](#-use-cases)

**Connect with fellow developers and AI enthusiasts!**

[![Join our Telegram Community](https://img.shields.io/badge/Join_Community-Telegram-blue?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/evi_run)

</div>

---

## 🌟 What is evi-run?

**evi-run** is a powerful, production-ready multi-agent AI system that bridges the gap between out-of-the-box solutions and custom AI frameworks. Built on Python using the OpenAI Agents SDK, the system has an intuitive interface via a Telegram bot and provides enterprise-level artificial intelligence capabilities.

### ✨ Key Advantages

- **🚀 Instant Deployment** - Get your AI system running in minutes, not hours
- **🔧 Ultimate Flexibility** - Framework-level customization capabilities
- **📊 Built-in Analytics** - Comprehensive usage tracking and insights
- **💬 Telegram Integration** - Seamless user experience through familiar messaging interface
- **🏗️ Scalable Architecture** - Grows with your needs from prototype to production

---

## 🎯 Features

### 🔮 Advanced System Features
- **Memory Management** - Context control and long-term memory
- **Knowledge Integration** - Dynamic knowledge base expansion
- **Task Scheduling** - Scheduling and deferred task execution / once / daily / interval /
- **Multi-Agent Orchestration** - Complex task decomposition and execution
- **Custom Agent Creation** - Build specialized AI agents for specific tasks

### 🦄 AI Features
- **Deep Research** - Multi-step investigation and analysis
- **Web Intelligence** - Smart internet search and data extraction
- **Document Processing** - Handle PDFs, images, and various file formats
- **Image Generation** - AI-powered visual content creation
- **DEX Analytics** - Real-time decentralized exchange monitoring
- **Solana Token Swap** - Easy, fast and secure token swap

**⚠️ Important for Token Swap:**
The token swap function is only active in private mode. Your private key will be stored in your database in base64 format.

### 💰 Flexible Usage Modes
- **Private Mode** - Personal use for bot owner only
- **Free Mode** - Public access with configurable usage limits
- **Pay Mode** - Monetized system with balance management and payments

### ⏳ Under Development
- **NSFW Mode** - Unrestricted topic exploration and content generation
- **Task Scheduler** - Automated agent task planning and execution / ✅ completed /
- **Automatic Limit Orders** - Smart trading with automated take-profit and stop-loss functionality

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Core Language** | Python 3.11 |
| **AI Framework** | OpenAI Agents SDK |
| **Communication** | Model Context Protocol |
| **Blockchain** | Solana RPC API |
| **Interface** | Telegram Bot API |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Deployment** | Docker & Docker Compose |

---

## 🚀 Quick Installation

Get evi-run running in under 5 minutes with our streamlined Docker setup:

### Prerequisites

**System Requirements:**
- Ubuntu 22.04 server (ensure location is not blocked by OpenAI)
- Root or sudo access
- Internet connection

**Required API Keys & Tokens:**
- **Telegram Bot Token** - Create bot via [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Your Telegram ID** - Get from [@userinfobot](https://t.me/userinfobot)

**⚠️ Important for Image Generation:**
To use protected OpenAI models (especially for image generation), you need to complete organization verification at [OpenAI Organization Settings](https://platform.openai.com/settings/organization/general). This is a simple verification process required by OpenAI.

### Installation Steps

1. **Download and prepare the project:**
   ```bash
   # Navigate to installation directory
   cd /opt
   
   # Clone the project from GitHub
   git clone https://github.com/pipedude/evi-run.git
   
   # Set proper permissions
   sudo chown -R $USER:$USER evi-run
   cd evi-run
   ```

2. **Configure environment variables:**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit configuration files
   nano .env          # Add your API keys and tokens
   nano config.py     # Set your Telegram ID and preferences
   ```

3. **Run automated Docker setup:**
   ```bash
   # Make setup script executable
   chmod +x docker_setup_en.sh
   
   # Run Docker installation
   ./docker_setup_en.sh
   ```

4. **Launch the system:**
   ```bash
   # Build and start containers
   docker compose up --build -d
   ```

5. **Verify installation:**
   ```bash
   # Check running containers
   docker compose ps
   
   # View logs
   docker compose logs -f
   ```

**🎉 That's it! Your evi-run system is now live. Open your Telegram bot and start chatting!**

---

## 🔧 Configuration

### Essential Configuration Files

#### `.env` - Environment Variables
```bash
# REQUIRED: Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# REQUIRED: OpenAI API Key
API_KEY_OPENAI=your_openai_api_key
```

#### `config.py` - System Settings
```python
# REQUIRED: Your Telegram User ID
ADMIN_ID = 123456789

# Usage Mode: 'private', 'free', or 'pay'
TYPE_USAGE = 'private'
```

### Usage Modes Explained

| Mode | Description | Best For |
|------|-------------|----------|
| **Private** | Bot owner only | Personal use, development, testing |
| **Free** | Public access with limits | Community projects, demos |
| **Pay** | Monetized with balance system | Commercial applications, SaaS |

**⚠️ Important for Pay mode:**
Pay mode enables monetization features. To activate this mode, the owner must burn a certain amount of $EVI tokens. The platform supports custom tokens created on the Solana blockchain for monetization purposes.

---

## 💡 Use Cases

### 🎭 Virtual Characters
Create engaging AI personalities for entertainment, education, or brand representation.

### 🛠️ Customer Support
Deploy intelligent support bots that understand context and provide helpful solutions.

### 👤 Personal AI Assistant
Build your own AI companion for productivity, research, and daily tasks.

### 📊 Data Analyst
Automate data processing, generate insights, and create reports from complex datasets.

### 💹 Trading Agent
Launch trading agents for DEX with real-time analytics.

### 🔧 Custom Solutions
Leverage the framework to build specialized AI agents for any domain or industry.

---

## 🏗️ Advanced Customization

### 🔬 Model Selection & Configuration

By default, the system is configured for optimal performance and low cost of use. For professional and specialized use cases, proper model selection is crucial for optimal performance and cost efficiency.

#### Customizing for Professional Deep Research

**For Deep Research and Complex Analysis:**
- **`o3-deep-research`** - Most powerful deep research model for complex multi-step research tasks
- **`o4-mini-deep-research`** - Faster, more affordable deep research model

For **maximum research capabilities** using specialized deep research models:

1. **Use o3-deep-research for most powerful analysis** in `bot/agents_tools/agents_.py`:
   ```python
   deep_agent = Agent(
       name="Deep Agent",
       model="o3-deep-research",  # Most powerful deep research model
       # ... instructions
   )
   ```

2. **Alternative: Use o4-mini-deep-research for cost-effective deep research:**
   ```python
   deep_agent = Agent(
       name="Deep Agent",
       model="o4-mini-deep-research",  # Faster, more affordable deep research
       # ... instructions
   )
   ```

3. **Update Main Agent instructions** to prevent summarization:
   - Locate the main agent instructions in the same file
   - Ensure the instruction includes: *"VERY IMPORTANT! Do not generalize the answers received from the deep_knowledge tool, especially for deep research, provide them to the user in full, in the user's language."*

#### Available Models

For the complete list of available models, capabilities, and pricing, see the **[OpenAI Models Documentation](https://platform.openai.com/docs/models)**.

### Adding Custom Agents

evi-run uses the **Agents** library with a multi-agent architecture where specialized agents are integrated as tools into the main agent. All agent configuration is centralized in:

```bash
bot/agents_tools/agents_.py
```

#### 🔧 Adding a Custom Agent

**1. Create the Agent**
```python
# Add after existing agents
custom_agent = Agent(
    name="Custom Agent",
    instructions="Your specialized agent instructions here...",
    model="gpt-5-mini",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="low"),
        extra_body={"text": {"verbosity": "medium"}}
    ),
    tools=[WebSearchTool(search_context_size="medium")]  # Optional tools
)
```

**2. Register as Tool in Main Agent**
```python
# In create_main_agent function, add to main_agent.tools list:
main_agent = Agent(
    # ... existing configuration
    tools=[
        # ... existing tools
        custom_agent.as_tool(
            tool_name="custom_function",
            tool_description="Description of what this agent does"
        ),
    ]
)
```

#### ⚙️ Customizing Agent Behavior

**Main Agent (Evi) Personality:**
Edit the detailed instructions in the `main_agent` instructions block:
  - Character profile and personality
  - Expertise areas
  - Communication style
  - Behavioral patterns

**Agent Parameters:**
- `name`: Agent identifier
- `instructions`: System prompt and behavior
- `model`: OpenAI model (`gpt-5`, `gpt-5-mini`, etc.)
- `model_settings`: Model settings (Reasoning, extra_body, etc.)
- `tools`: Available tools (WebSearchTool, FileSearchTool, etc.)
- `mcp_servers`: MCP server connections

#### 🤖 Using Alternative Models

evi-run supports non-OpenAI models through the Agents library. There are several ways to integrate other LLM providers:

**Method 1: LiteLLM Integration (Recommended)**

Install the LiteLLM dependency:
```bash
pip install "openai-agents[litellm]"
```

Use models with the `litellm/` prefix:
```python
# Claude via LiteLLM
claude_agent = Agent(
    name="Claude Agent",
    instructions="Your instructions here...",
    model="litellm/anthropic/claude-3-5-sonnet-20240620",
    # ... other parameters
)

# Gemini via LiteLLM  
gemini_agent = Agent(
    name="Gemini Agent",
    instructions="Your instructions here...",
    model="litellm/gemini/gemini-2.5-flash-preview-04-17",
    # ... other parameters
)
```

**Method 2: LitellmModel Class**
```python
from agents.extensions.models.litellm_model import LitellmModel

custom_agent = Agent(
    name="Custom Agent",
    instructions="Your instructions here...",
    model=LitellmModel(model="anthropic/claude-3-5-sonnet-20240620", api_key="your-api-key"),
    # ... other parameters
)
```

**Method 3: Global OpenAI Client**
```python
from agents.models._openai_shared import set_default_openai_client
from openai import AsyncOpenAI

# For providers with OpenAI-compatible API
set_default_openai_client(AsyncOpenAI(
    base_url="https://api.provider.com/v1",
    api_key="your-api-key"
))
```

**Documentation & Resources:**
- **[Model Configuration Guide](https://openai.github.io/openai-agents-python/models/)** - Complete setup documentation
- **[LiteLLM Integration](https://openai.github.io/openai-agents-python/models/litellm/)** - Detailed LiteLLM usage
- **[Supported Models](https://docs.litellm.ai/docs/providers)** - Full list of LiteLLM providers

**Important Notes:**
- Most LLM providers don't support the Responses API yet
- If not using OpenAI, consider disabling tracing: `set_tracing_disabled()`
- You can mix different providers for different agents

#### 🎯 Best Practices

- **Focused Instructions**: Each agent should have a clear, specific purpose
- **Model Selection**: Use appropriate models for complexity (gpt-5 vs gpt-5-mini)
- **Tool Integration**: Leverage WebSearchTool, FileSearchTool, and MCP servers
- **Naming Convention**: Use descriptive tool names for main agent clarity
- **Testing**: Test agent responses in isolation before integration

#### 🌐 Bot Messages Localization

**Customizing Bot Interface Messages:**

All bot messages and interface text are stored in the `I18N` directory and can be fully customized to match your needs:

```
I18N/
├── factory.py          # Translation loader
├── en/
│   └── txt.ftl        # English messages
└── ru/
    └── txt.ftl        # Russian messages
```

**Message Files Format:**
The bot uses [Fluent](https://projectfluent.org/) localization format (`.ftl` files) for multi-language support:

**To customize messages:**
1. Edit the appropriate `.ftl` file in `I18N/en/` or `I18N/ru/`
2. Restart the bot container for changes to take effect
3. Add new languages by creating new subdirectories with `txt.ftl` files

---

## 📊 Monitoring & Analytics

evi-run includes comprehensive tracing and analytics capabilities through the OpenAI Agents SDK. The system automatically tracks all agent operations and provides detailed insights into performance and usage.

### 🔍 Built-in Tracing

**Automatic Tracking:**
- **Agent Runs** - Each agent execution with timing and results
- **LLM Generations** - Model calls with inputs/outputs and token usage
- **Function Calls** - Tool usage and execution details
- **Handoffs** - Agent-to-agent interactions
- **Audio Processing** - Speech-to-text and text-to-speech operations
- **Guardrails** - Safety checks and validations

**⚠️ Important for enabled Tracing:**
The OpenAI Agents SDK (Tracing) analytics system records all user requests for performance monitoring. Although the data is anonymized, this creates privacy issues.

For ethical reasons, owners of public bots should either explicitly inform users about this, or disable Tracing.

```python
# Disable Tracking in `bot/agents_tools/agents_.py`
set_tracing_disabled(True)
```

### 📈 External Analytics Platforms

evi-run supports integration with 20+ monitoring and analytics platforms:

**Popular Integrations:**
- **[Weights & Biases](https://weave-docs.wandb.ai/guides/integrations/openai_agents)** - ML experiment tracking
- **[LangSmith](https://docs.smith.langchain.com/observability/how_to_guides/trace_with_openai_agents_sdk)** - LLM application monitoring
- **[Arize Phoenix](https://docs.arize.com/phoenix/tracing/integrations-tracing/openai-agents-sdk)** - AI observability
- **[Langfuse](https://langfuse.com/docs/integrations/openaiagentssdk/openai-agents)** - LLM analytics
- **[AgentOps](https://docs.agentops.ai/v1/integrations/agentssdk)** - Agent performance tracking
- **[Pydantic Logfire](https://logfire.pydantic.dev/docs/integrations/llms/openai/)** - Structured logging

**Enterprise Solutions:**
- **[Braintrust](https://braintrust.dev/docs/guides/traces/integrations)** - AI evaluation platform
- **[MLflow](https://mlflow.org/docs/latest/tracing/integrations/openai-agent)** - ML lifecycle management
- **[Portkey AI](https://portkey.ai/docs/integrations/agents/openai-agents)** - AI gateway and monitoring

### 📋 System Logs

**Docker Container Logs:**
```bash
# View all logs
docker compose logs

# Follow specific service
docker compose logs -f bot

# Database logs
docker compose logs postgres_agent_db

# Filter by time
docker compose logs --since 1h bot
```

### 🔗 Documentation

- **[Complete Tracing Guide](https://openai.github.io/openai-agents-python/tracing/)** - Full tracing documentation
- **[Analytics Integration List](https://openai.github.io/openai-agents-python/tracing/#external-tracing-processors-list)** - All supported platforms

---

## 🔍 Troubleshooting

### Common Issues

**Bot not responding:**
```bash
# Check bot container status
docker compose ps
docker compose logs bot
```

**Database connection errors:**
```bash
# Restart database
docker compose restart postgres_agent_db
docker compose logs postgres_agent_db
```

**Memory issues:**
```bash
# Check system resources
docker stats
```

### Support Resources
- **Community**: [Telegram Support Group](https://t.me/evi_run)
- **Issues**: [GitHub Issues](https://github.com/pipedude/evi-run/issues)
- **Telegram**: [@playa3000](https://t.me/playa3000)

---

## 🚦 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 10GB
- **Network**: Stable internet connection

### Recommended for Production
- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Storage**: 20GB+ SSD
- **Network**: High-speed connection

---

## 🔐 Security Considerations

- **API Keys**: Store securely in environment variables
- **Database**: Use strong passwords and restrict access
- **Network**: Configure firewalls and use HTTPS
- **Updates**: Keep dependencies and Docker images updated

---

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

---

## 👽 Community and Support

- **Website**: [evi.run](https://evi.run)
- **Contact**: [Alex Flash](https://t.me/playa3000)
- **Community**: [Telegram Group](https://t.me/evi_run)
- **X (Twitter)**: [alexflash99](https://x.com/alexflash99)
- **Reddit**: [Alex Flash](https://www.reddit.com/user/Worth_Professor_425/)

---

<div align="center">

**Made with ❤️ by the evi-run team**

⭐ **Star this repository if evi-run helped you build amazing AI experiences!** ⭐

</div>
