import os
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from Assistant.agent import sigma_agent
from google.genai import types
from AgentSimple.agent_simple import agent2

import warnings

warnings.filterwarnings("ignore")

import logging

logging.basicConfig(level=logging.ERROR)

session_service = InMemorySessionService()

APP_NAME = "python_assistant"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def init_session(app_name: str, user_id: str, session_id: str) -> InMemorySessionService:
    sesh = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return sesh


session = asyncio.run(init_session(APP_NAME, USER_ID, SESSION_ID))

runner = Runner(
    agent=sigma_agent,
    app_name=APP_NAME,
    session_service=session_service
)
print(f"Runner created for agent '{runner.agent.name}'.")


async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # Sprawdzamy, czy to odpowiedź końcowa od dowolnego sub-agenta
        if event.is_final_response():
            if event.content and event.content.parts:
                # Nadpisujemy - ostatni agent w SequentialAgent (final_presenter)
                # będzie tym, którego wynik zobaczymy na końcu.
                final_response_text = event.content.parts[0].text
                print(f"[Debug] Agent finished with: {final_response_text}")

            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No message.'}"

        # NIE używamy tutaj 'break', aby pętla przeszła przez wszystkie kroki SequentialAgent

    print(f"\n<<< Final Agent Result: {final_response_text}")


async def run_conversation():
    await call_agent_async("Install nano",
                           runner=runner,
                           user_id=USER_ID,
                           session_id=SESSION_ID)


if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")
