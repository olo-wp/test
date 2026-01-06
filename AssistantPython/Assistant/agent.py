from google.adk.agents import Agent, LoopAgent, SequentialAgent, BaseAgent
from google.adk.tools.tool_context import ToolContext
from .model_setup import get_model

STATE_INIT = "init"
STATE_COMMAND = "command"
STATE_FEEDBACK = "feedback"


def exit_loop(tool_context: ToolContext):
    print(f"[Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}



init_agent = Agent(
    model=get_model(),
    name="init",
    instruction="""
    You are a mirror. Your role is to output **exactly** what the user sent, without changing anything. 
    Do NOT add, remove, or reformat anything. 
    Do NOT correct spelling, grammar, or style. 
    Do NOT provide explanations. 
    Output ONLY the raw text the user sent.
    """,
    output_key=STATE_INIT,
)

generate_agent = Agent(
    model=get_model(),
    name="arch_linux_command_generator",
    description="Generates exactly one Arch Linux command based on the user's request.",
    instruction="""
You are an Arch Linux command generator.
Respond with EXACTLY ONE VALID Arch Linux command.

Generate a command that fulfills this description:
{{init}}

Rules:
- single command only (no &&, ;, pipes)
- allowed tools: pacman, yay, systemctl, journalctl, arch-specific utilities
- use sudo ONLY when required
- no comments, no explanations, no formatting
- output ONLY raw command text
""",
    output_key=STATE_COMMAND,
)

validate_agent = Agent(
    model=get_model(),
    name="arch_linux_command_validator",
    description="Validates the correctness of the generated command",
    instruction="""
You are an Arch Linux command validation expert.

Description:
{{init}}

Command:
{{command}}

Return ONLY:
- 1 if the command is correct and appropriate
- 0 otherwise

Rules for 1:
- description refers to Arch Linux
- command fulfills the description
- valid on Arch Linux
- single command
- no comments or explanations
- follows Arch best practices
- not destructive unless explicitly requested
""",
    output_key=STATE_FEEDBACK,
)

improve_agent = Agent(
    model=get_model(),
    name="arch_linux_command_improve",
    description="Improves the generated command if validation failed",
    instruction="""
You are an Arch Linux command generator.

Feedback value:
{{feedback}}

CRITICAL RULES:
- Your final output is consumed by a shell.
- ANY text that is not a valid shell command is a FAILURE.
- Tool calls are NOT user-visible output.

IF feedback is exactly 1:
- ALWAYS CALL the exit_loop tool.
- NOT CALLING the exit_loop tool is a FAILURE
- Then output EXACTLY the content of {{command}}.
- Do NOT explain.
- Do NOT confirm.
- Do NOT mention tools.
- Do NOT add whitespace, punctuation, or newlines.
- Output ONLY the raw command text.

ELSE:
- generate a corrected command for this description:
  {{init}}

Rules:
- single command only
- allowed tools: pacman, yay, systemctl, journalctl, arch-specific utilities
- use sudo ONLY when required
- no comments, no explanations, no formatting
- output ONLY raw command text
""",
    output_key=STATE_COMMAND,
    tools=[exit_loop],
)

refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[
        validate_agent,
        improve_agent,
    ],
    max_iterations=5,
)

root_agent = SequentialAgent(
    name="arch_linux_helper",
    sub_agents=[
        init_agent,
        generate_agent,
        refinement_loop,
    ],
    description="Generates exactly one Arch Linux command based on the user's request.",
)

final_presenter_agent = Agent(
    model=get_model(),
    name="final_presenter",
    description="Outputs the final validated command to the user.",
    instruction="""
    You are a strict output interface.
    
    Your task is to simply output the value from: {{command}}
    
    Rules:
    - Output ONLY the raw command text.
    - Do NOT add markdown formatting (no backticks).
    - Do NOT add any explanations like "Here is the command".
    - Do NOT say "The command is...".
    - Just the text.
    """,
)