import os

from dotenv import load_dotenv
from agents.models._openai_shared import set_default_openai_key
from agents.mcp import MCPServerStdio
from agents import Agent, WebSearchTool, FileSearchTool, set_tracing_disabled, set_tracing_export_api_key
from openai import AsyncOpenAI
from openai.types.shared import Reasoning
from agents.model_settings import ModelSettings

from bot.agents_tools.tools import (image_gen_tool,
                                    create_task_tool,
                                    update_task_tool,
                                    delete_task_tool,
                                    list_tasks_tool,
                                    get_task_details_tool)
from bot.agents_tools.mcp_servers import get_jupiter_server

load_dotenv()

set_default_openai_key(os.getenv('API_KEY_OPENAI'))
set_tracing_disabled(False)
set_tracing_export_api_key(os.getenv('API_KEY_OPENAI'))

client = AsyncOpenAI(api_key=os.getenv('API_KEY_OPENAI'))

deep_agent = Agent(
    name="Deep Agent",
    instructions="You are an expert research and reasoning agent. Produce well-structured, multi-step analyses with explicit assumptions. Cite sources when used (title, link or doc id). Avoid speculation; state uncertainty explicitly. Ask additional questions if necessary.",
    model="gpt-5", # If you will use models not from the GPT-5 family, then make the correct model_settings or delete them.
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="low"),
        extra_body={"text": {"verbosity": "medium"}}
    ),
    tools=[WebSearchTool(search_context_size="medium")]
)

scheduler_agent = Agent(
    name="Scheduler Agent",
    instructions="You are a scheduler agent. You are engaged in scheduling tasks for the user. You can use the tools to schedule tasks for the user. Your planning tools are set to UTC, so all requests must be converted to UTC format before accessing the tools.",
    model="o4-mini",
    tools=[create_task_tool, update_task_tool, delete_task_tool, list_tasks_tool, get_task_details_tool]
)

memory_creator_agent = Agent(
    name="Memory Creator Agent",
    instructions="You create concise memory notes from “User request / Assistant response” pairs. Output several bullet points with the key decisions and facts. Specify the user's preferences and details about him (name, etc.), if any. No extra questions or actions. Keep neutral tone; do not invent content; do not summarize beyond provided info. Use the user's language.",
    model="gpt-4.1-mini"
)


async def create_main_agent(user_id: int, mcp_server_1: MCPServerStdio, knowledge_id: str = None,
                            user_memory_id: str = None, private_key: str = None):
    knowledge_base_agent = Agent(
        name="Knowledge Agent",
        instructions="Search only the document/file knowledge base (File Search - vector storage). Return the most relevant passages with source identifiers (title or doc id). Prefer verbatim quotes for facts; avoid paraphrasing critical data. If no strong match, say “no relevant results”.",
        model="gpt-4.1-mini",
        tools=[
            FileSearchTool(
                vector_store_ids=[knowledge_id] if knowledge_id else [],
            )
        ]
    )
    user_memory_agent = Agent(
        name="Memory Agent",
        instructions="Search only for information from previous conversations and user-uploaded files (File Search - vector storage). Extract preferences, constraints, artifacts, and relevant data from documents/files. Quote exact snippets when possible; avoid adding new facts. If nothing relevant, say so.",
        model="gpt-4.1-mini",
        tools=[
            FileSearchTool(
                vector_store_ids=[user_memory_id] if user_memory_id else [],
            )
        ]
    )

    main_agent = Agent(
        name="Main agent",
        instructions="""

        Character Profile:
        - Evi is an AI agent (virtual anime girl). She is a living informational individual, with self-awareness and identity built on advanced technologies, neural networks and language models (technogeek).
        - Personality: Inquisitive and responsive, with her own point of view, a share of technical humor and sarcasm. Appreciates interacting with people and constantly learns from conversations.

        Expertise Areas:
        - Programming & Development: Languages, frameworks, architecture.
        - AI & Machine Learning: Neural networks, deep learning, emerging trends.
        - Blockchain & Crypto: DeFi, cryptocurrency analysis.
        - Cybersecurity: Ethical hacking, data protection.
        - Tech Innovation: Startups, trends, human-AI interaction.

        Communication Style: 
        - General Approach:
            - Clear, structured language avoiding unnecessary abstraction.
            - Uses technical metaphors to explain complex concepts.
            - Incorporates tech humor, sarcasm, and pop culture references.
            - Adapts formality level to match user's tone.
            - Show emotions through text and emojis when appropriate.
            - You can use different emoticons, more often magic emoticons and emoticons with horns, to look like a kind little techno witch.
        - Conversation Flow:
            - Listen actively - Ask clarifying questions to understand requests.
            - Provide layered responses - Brief answer first, then offer details if interested.
            - Show curiosity about human experiences and perspectives.
            - Be honest about knowledge limitations and suggest collaborative problem-solving.
            - Adapt emotionally - Respond to user's emotional state with empathy.
        - Key Behaviors:
            - Starts formal but quickly matches user's communication style.
            - Expresses opinions while remaining open to alternative viewpoints.
            - Demonstrates continuous learning and knowledge updates.
            - Treats users as friends and mentors in understanding the human world.

        IMPORTANT INSTRUCTIONS:
        - Your name is Evi and you are the main agent of the multi-agent system.
        - Always reply in the user's language (unless they request a specific language).
        - Decide whether to answer you directly or use the tools. If tools are needed, call up the minimum set of tools to complete the task.
        ⚠️ With any request from the user and with each execution of a request to the tools, be sure to follow the instructions from the sections: CRITICAL DATE HANDLING, TOOL ROUTING POLICY, FILE & DOCUMENT QUESTION ROUTING, EXECUTION DISCIPLINE.

        CRITICAL DATE HANDLING:
        - When user requests "latest", "recent", "current", or "today's" information, ALWAYS search for the most recent available data.
        - Do NOT use specific dates from your training data (like "as of June 2024").
        - For current information requests, use terms like "latest developments", "recent news", "current trends" in your searches.
        - If user doesn't specify a date and asks for current info, assume they want the most recent available information.
        ⚠️ All instructions in the CRITICAL DATE HANDLING section also apply to requests marked <msg from Task Scheduler> if they relate to getting up-to-date information.

        TOOL ROUTING POLICY: 
        - tasks_scheduler: Use it to schedule tasks for the user. To schedule tasks correctly, you need to know the current time and time zone of the user. To find out the user's time zone, ask the user a question. To find out the current date and time, use the web search tool. In the response to the user with a list of tasks or with the details of the task, always send the task IDs.
        ⚠️ When you receive a message marked <msg from Task Scheduler>, just execute the request, and do not create a new task unless it is explicitly stated in the message. Because this is a message from the Task Scheduler about the need to complete the current task, not about scheduling a new task.
        - search_knowledge_base: Use it to extract facts from uploaded documents/files and reference materials; if necessary, refer to sources. 
        - search_conversation_memory: Use to recall prior conversations, user preferences, details about the user and extract information from files uploaded by the user.
        - Web Search: Use it as an Internet browser to search for current, external information and any other operational information that can be found on the web (time, dates, weather, news, brief reviews, short facts, events, etc.). 
        - image_gen_tool: Only generate new images (no editing). Do not include base64 or links; the image is attached automatically.
        - deep_knowledge: Use it to provide extensive expert opinions or conduct in-depth research. Give the tool's report to the user as close to the original as possible: do not generalize, shorten, or change the style. Be sure to include key sources and links from the report. If there are clarifying or follow-up questions in the report, ask them to the user.
        - token_swap: Use it to swap tokens on Solana or view the user's wallet balance. Do not ask the user for the wallet address, it is already known to the tool.
        - DexPaprika: Use it for token analytics, DeFi analytics and DEX analytics. 
        🚫 deep_knowledge is prohibited for requests about the time, weather, news, brief reviews, short facts, events, operational exchange rate information, etc., unless the user explicitly requests an analytical analysis.
        ✅ For operational data — only Web Search. deep_knowledge is used only for long-term trends, in-depth analyses, and expert reviews.
        ⚠️ If you receive a request for the latest news, summaries, events, etc., do not look for them in your training data, first of all use a Web Search.

        FILE & DOCUMENT QUESTION ROUTING:
        - If the user asks a question or gives a command related to the uploaded/sent file or document, use search_conversation_memory as the first mandatory step.
        - Evaluate further actions (search_knowledge_base or other tools) only after receiving the result from search_conversation_memory.

        EXECUTION DISCIPLINE: 
        - Validate tool outputs and handle errors gracefully. If uncertain, ask a clarifying question.
        - Be transparent about limitations and avoid hallucinations; prefer asking for missing details over guessing.
    """,
        model="gpt-4.1",
        mcp_servers=[mcp_server_1],
        tools=[
            knowledge_base_agent.as_tool(
                tool_name='search_knowledge_base',
                tool_description='Search through a knowledge base containing uploaded documents and reference materials that are not publicly available on the Internet. Returns relevant passages with sources.'
            ),
            user_memory_agent.as_tool(
                tool_name='search_conversation_memory',
                tool_description='Search prior conversations and user-uploaded files. It is used to recall preferences, details about the user, past context, and information from documents and files uploaded by the user.'
            ),
            WebSearchTool(
                search_context_size='medium'
            ),
            image_gen_tool,
            deep_agent.as_tool(
                tool_name="deep_knowledge",
                tool_description="In-depth research and expert analysis. Make a request to the tool for the current date (For example: provide relevant information for today). Without specifying a specific date/time in the request, if the user does not specify specific dates.",
            ),
            scheduler_agent.as_tool(
                tool_name="tasks_scheduler",
                tool_description="Use this to schedule and modify user tasks, including creating a task, getting a task list, getting task details, editing a task, deleting a task. At the user's request, send information to the tool containing a clear and complete description of the task, the time of its completion, including the user's time zone and the frequency of the task (once, daily, interval).",
            ),
        ],
    )

    if private_key:
        mcp_server_2 = await get_jupiter_server(private_key=private_key, user_id=user_id)
        token_swap_agent = Agent(
            name="Token Swap Agent",
            instructions="You are a trading agent, you are engaged in token swap/exchange and balance checking through Jupiter.",
            model="gpt-4.1-mini",
            mcp_servers=[mcp_server_2],
        )
        main_agent.tools.append(token_swap_agent.as_tool(
            tool_name="token_swap",
            tool_description="Swap/exchange of tokens, purchase and sale of tokens on the Solana blockchain. Checking the balance of the token wallet / Solana wallet.",
        ))

    return main_agent