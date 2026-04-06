# models.py
from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
from openenv.core.env_server import Action, Observation, State

class ActionType(str, Enum):
    SEARCH_KB        = "search_kb"         # Search knowledge base
    LOOKUP_ORDER     = "lookup_order"      # Pull order details
    CHECK_ACCOUNT    = "check_account"     # Pull account status/flags
    PROCESS_REFUND   = "process_refund"    # Issue a refund
    FLAG_SECURITY    = "flag_security"     # Raise security alert
    ASK_USER         = "ask_user"          # Ask clarifying question
    SEND_RESPONSE    = "send_response"     # Send message to user
    ESCALATE         = "escalate"          # Escalate to human/specialist
    RESOLVE          = "resolve"           # Mark ticket as resolved
    CLOSE_NO_ACTION  = "close_no_action"   # Close without action (spam etc.)


class SupportAction(Action):
    """What the agent does each step."""
    action_type: ActionType
    # Freeform parameter: query text, order ID, reason, message, etc.
    action_value: str = ""


class ToolResult(object):
    """Returned by tools — included in observation."""
    pass


class SupportObservation(Observation):
    """What the agent sees after each step. done + reward inherited."""
    # Static ticket context (never changes within episode)
    ticket_id: str
    ticket_text: str
    user_id: str
    account_tier: str              # "free" | "premium" | "enterprise"
    account_age_days: int

    # Dynamic state (updates each step)
    conversation_history: List[Dict[str, str]]   # role + content pairs
    tool_results: List[Dict[str, Any]]            # results from tool calls
    policy_violations: List[str]                  # policies breached so far
    resolved: bool
    step_number: int
    steps_remaining: int

    # Feedback from last action
    last_feedback: str
    cumulative_reward: float


class SupportState(State):
    """Internal state — episode_id + step_count inherited."""
    task_id: str = ""
    task_difficulty: str = "easy"       # easy | medium | hard
    true_resolution: str = ""           # ground truth expected resolution
    required_tools: List[str] = []      # tools that SHOULD be called
    forbidden_actions: List[str] = []   # actions that violate policy
    max_steps: int = 15
    total_reward: float = 0.0
    tools_used: List[str] = []
    policy_violations: List[str] = []
    resolved: bool = False
    resolution_correct: bool = False