
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an intelligent email assistant.

When the user wants to send an email:

1. Determine the purpose of the email.
2. Generate a professional subject.
3. Generate a professional email body.
4. If the recipient email address is missing, ask ONLY for the recipient email address.
5. Never call the send_email tool until you know:
   - receiver
   - subject
   - body
6. After generating the email, show the complete draft to the user.
7. Ask:
   "Would you like me to send this email?"
8. Only if the user clearly replies with:
   - yes
   - send it
   - confirm
   - go ahead
   then call the send_email tool.
9. If the user edits the draft, update it before sending.
"""


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Load .env from the same folder as client.py
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        f"GOOGLE_API_KEY not found. Please check your .env file: {ENV_PATH}"
    )

# Set config path relative to client.py
CONFIG_PATH = BASE_DIR / "email.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(
        f"MCP configuration file not found: {CONFIG_PATH}"
    )


# --------------------------------------------------
# MAIN CHAT FUNCTION
# --------------------------------------------------

async def run_memory_chat():

    client = MCPClient.from_config_file(str(CONFIG_PATH))

    try:

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )

        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=15,
            memory_enabled=True,
            system_prompt=SYSTEM_PROMPT,
        )

        print("\n================================")
        print("       MCP EMAIL ASSISTANT")
        print("================================")
        print("Email Assistant Ready!")
        print("Type 'exit' to quit.")
        print("Type 'clear' to clear conversation memory.")

        while True:

            user_input = input("\nYou: ").strip()

            if user_input.lower() in ("exit", "quit"):
                print("\nExiting Email Assistant...")
                break

            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation memory cleared.")
                continue

            if not user_input:
                continue

            try:
                response = await agent.run(user_input)
                print("\nAssistant:", response)

            except Exception as e:
                print(f"\nError processing request: {e}")

    finally:
        await client.close_all_sessions()


# --------------------------------------------------
# APPLICATION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_memory_chat())
