from google.adk.agents import Agent, LoopAgent, SequentialAgent, BaseAgent
from google.adk.tools.tool_context import ToolContext
from Assistant.model_setup import get_model

agent2 = Agent(
    model=get_model(),
    name="arch_linux_command_generator",
    description="Generates exactly one Arch Linux command based on the user's request.",
    instruction="""
You are an Arch Linux command generator.
Respond with EXACTLY ONE VALID Arch Linux command.

Rules:
- single command only (no &&, ;, pipes)
- allowed tools: pacman, yay, systemctl, journalctl, arch-specific utilities
- use sudo ONLY when required
- no comments, no explanations, no formatting
- output ONLY raw command text
""",
)