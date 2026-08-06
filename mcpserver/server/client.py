import asyncio
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from mcp_use import MCPAgent, MCPClient


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
6. After generating the email, show the draft to the user.
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


async def run_memory_chat():

    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    client = MCPClient.from_config_file("server/email.json")

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
    )

    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,
        system_prompt=SYSTEM_PROMPT,
    )

    print("Email Assistant Ready")

    try:
        while True:

            user_input = input("\nYou: ")

            if user_input.lower() in ("exit", "quit"):
                break

            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                continue

            response = await agent.run(user_input)

            print("\nAssistant:", response)

    finally:
        await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())