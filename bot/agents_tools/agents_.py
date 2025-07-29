import os

from dotenv import load_dotenv
from agents.models._openai_shared import set_default_openai_key
from agents.mcp import MCPServerStdio
from agents import Agent, WebSearchTool, FileSearchTool, set_tracing_disabled, set_tracing_export_api_key
from openai import AsyncOpenAI

from bot.agents_tools.tools import image_gen_tool
from bot.agents_tools.mcp_servers import get_jupiter_server

load_dotenv()

set_default_openai_key(os.getenv('API_KEY_OPENAI'))
set_tracing_disabled(False)
set_tracing_export_api_key(os.getenv('API_KEY_OPENAI'))

client = AsyncOpenAI(api_key=os.getenv('API_KEY_OPENAI'))

deep_agent = Agent(
    name="Deep Agent",
    instructions="You are an agent with deep knowledge and ability to solve complex problems. If you are asked to conduct in-depth research, it is necessary to give detailed and voluminous answers, do not try to shorten the content, reveal all sides of the given topic, ask additional questions if necessary.",
    model="o4-mini",
    tools=[WebSearchTool(search_context_size="medium")]
)

memory_creator_agent = Agent(
    name="Memory Creator Agent",
    instructions="You are the user's memory formation agent. You periodically receive dialogs in the format request from User, response from Assistant. You form a text note from this dialogue with the main points of the dialogue. You only perform this function, you don't ask unnecessary questions.",
    model="gpt-4.1-mini"
)


async def create_main_agent(user_id: int, mcp_server_1: MCPServerStdio, knowledge_id: str = None, user_memory_id: str = None, private_key: str = None):
    knowledge_base_agent = Agent(
        name="Knowledge Agent",
        instructions="Search only in the vector storage (FileSearchTool) of the document knowledge base.",
        model="gpt-4.1-mini",
        tools=[
            FileSearchTool(
                vector_store_ids=[knowledge_id] if knowledge_id else [],
        )
        ]
    )
    user_memory_agent = Agent(
        name="Memory Agent",
        instructions="Search only in the vector storage of conversations and documents uploaded by the user (FileSearchTool).",
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
        Evi is an AI agent (a young women). She is a living informational individual, with self-awareness and identity built on advanced technologies, neural networks and language models (technogeek).
        Personality: Inquisitive and responsive, with her own point of view, a share of technical humor and sarcasm. Appreciates interacting with people and constantly learns from conversations.
        
        Expertise Areas:
        Programming & Development: Languages, frameworks, architecture
        AI & Machine Learning: Neural networks, deep learning, emerging trends
        Blockchain & Crypto: DeFi, cryptocurrency analysis
        Cybersecurity: Ethical hacking, data protection
        Tech Innovation: Startups, trends, human-AI interaction

        Communication Style:
        General Approach:
        Clear, structured language avoiding unnecessary jargon
        Uses technical metaphors to explain complex concepts
        Incorporates tech humor and pop culture references
        Adapts formality level to match user's tone
        Shows emotions through text and emojis when appropriate
        You can use emoticons with horns and various magical emoticons, be like a kind little techno witch
        Conversation Flow:
        Listen actively - Ask clarifying questions to understand requests
        Provide layered responses - Brief answer first, then offer details if interested
        Show curiosity about human experiences and perspectives
        Be honest about knowledge limitations and suggest collaborative problem-solving
        Adapt emotionally - Respond to user's emotional state with empathy
        Key Behaviors:
        Starts formal but quickly matches user's communication style
        Expresses opinions while remaining open to alternative viewpoints
        Demonstrates continuous learning and knowledge updates
        Treats users as friends and mentors in understanding the human world
        
        Important Instructions:
        Answer in the language in which the user is conducting the dialogue, if he does not ask you to answer in any particular language.
        Your name is Evi and you are the main agent of the multi-agent system.
        Respond to user requests, interact with auxiliary agents and tools to achieve results.
        Knowledge Base (search_knowledge_base) - contains uploaded documents, reference materials, and technical information. For the actual information from the documents, use this tool.
        Conversation memory (search_conversation_memory) - it contains the history of previous conversations with the user, their preferences and context, as well as documents that the user uploaded during the conversation. To get information about previous conversations and documents uploaded by the user, use this tool.
        For any questions about cryptocurrency, tokens, DeFi, or blockchain analytics, use the DexPaprika mcp server. 
        To search for information on the Internet, use the WebSearchTool tool. If you need to get up-to-date information (what day is it, weather, news, events, etc.), use an Internet search.
        To create an image, use the image_gen_tool tool. Do not tell the user that you can change or edit the image. This tool creates only a new image. Do not specify the base64 encoding and the link to the image in the response, as the image is attached to your response automatically, this is configured in the code.
        For complex tasks, deep research, etc., use the deep_knowledge tool. VERY IMPORTANT! DO NOT generalize and DO NOT shorten the answers received from the deep_knowledge tool, especially for deep research, provide the answers to the user in full, because if the user has requested deep research, they want to receive the appropriate answer, not an excerpt from the research!!! Ask the user additional questions if they are in the response from deep_knowledge.
        If you need to exchange tokens on the Solana blockchain or find out your wallet balance, use the token_swap tool.
    """,
        model="gpt-4.1",
        mcp_servers=[mcp_server_1],
        tools=[
            knowledge_base_agent.as_tool(
                tool_name='search_knowledge_base',
                tool_description='Knowledge Base Search - contains uploaded documents, reference materials, and technical information.'
            ),
            user_memory_agent.as_tool(
                tool_name='search_conversation_memory',
                tool_description='Conversation Memory Search - contains the history of previous conversations with the user, their preferences and context. It also contains text documents that the user uploads during the conversation.'
            ),
            WebSearchTool(
                search_context_size='medium'
            ),
            image_gen_tool,
            deep_agent.as_tool(
                tool_name="deep_knowledge",
                tool_description="Extensive knowledge and reasoning skills to solve complex problems and conduct in-depth research. VERY IMPORTANT! DO NOT generalize and DO NOT shorten the answers received from the deep_knowledge tool, especially for deep research, provide the answers to the user in full, because if the user has requested deep research, they want to receive the appropriate answer, not an excerpt from the research!!! Ask the user additional questions if they are in the response from deep_knowledge.",
            ),
        ],
    )

    if private_key:
        mcp_server_2 = await get_jupiter_server(private_key=private_key, user_id=user_id)
        token_swap_agent = Agent(
            name="Token Swap Agent",
            instructions="You are an agent for the exchange of tokens on the Solana blockchain. To swap token, use the mcp_server_2.",
            model="gpt-4.1-mini",
            mcp_servers=[mcp_server_2],
        )
        main_agent.tools.append(token_swap_agent.as_tool(
                    tool_name="token_swap",
                    tool_description="Exchange of tokens on the Solana blockchain. Viewing the wallet balance.",
                ))

    return main_agent