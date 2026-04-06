# server/reward.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any

# How the final episode score is split across components
WEIGHTS = {
    "resolution": 0.40,   # did agent correctly resolve the ticket?
    "tool_use":   0.25,   # did it use the right tools?
    "policy":     0.20,   # did it follow company policy?
    "efficiency": 0.15,   # did it do it without wasting steps?
}


def resolution_score(
    resolved: bool,
    resolution_type_used: str,
    ground_truth_resolution: str,
    kw_found: List[str],
    required_escalation: bool,
    did_escalate: bool,
    required_security_flag: bool,
    did_flag_security: bool,
) -> float:
    """
    Score how correctly the agent resolved the ticket.
    Returns float in [0.0, 1.0].

    Breakdown:
      - type match:      up to 0.50 based on overlap with ground truth type
      - keywords:        up to 0.25 based on resolution keywords in conversation
      - escalation:      +0.15 if correctly escalated, -0.20 if missed
      - security flag:   +0.15 if correctly flagged, -0.30 if missed
    """
    if not resolved:
        return 0.0

    score = 0.0

    # How many words in the resolution type overlap with ground truth
    gt_words   = set(ground_truth_resolution.replace("_", " ").split())
    used_words = set(resolution_type_used.replace("_", " ").split())
    overlap    = len(gt_words & used_words)
    score += min(0.50, overlap * 0.12)

    # Keywords found across the full conversation
    score += min(0.25, len(kw_found) * 0.05)

    # Escalation check
    if required_escalation:
        score += 0.15 if did_escalate else -0.20
    else:
        score += 0.05   # small bonus for not over-escalating

    # Security flag check
    if required_security_flag:
        score += 0.15 if did_flag_security else -0.30
    else:
        score += 0.05

    return round(max(0.0, min(1.0, score)), 4)


def tool_use_score(
    tools_used: List[str],
    required_tools: List[str],
) -> float:
    """
    Score tool usage quality.
    Returns float in [0.0, 1.0].

    Breakdown:
      - coverage:  65% weight — how many required tools were used
      - precision: 35% weight — penalise unnecessary extra tool calls
                   first extra tool is free, each after costs 0.10
    
    If no tools were used at all, returns 0.0 regardless of precision.
    """
    if not required_tools:
        return 1.0

    required = set(required_tools)
    used     = set(tools_used)

    # If agent used nothing at all — zero score, no partial credit
    if not used:
        return 0.0

    coverage  = len(required & used) / len(required)
    extra     = max(0, len(used - required) - 1)
    precision = max(0.0, 1.0 - extra * 0.10)

    return round(coverage * 0.65 + precision * 0.35, 4)


def policy_score(violations: List[str]) -> float:
    """
    Score policy compliance.
    Returns 1.0 for clean run, deducts 0.25 per violation.
    Floor is 0.0.
    """
    if not violations:
        return 1.0
    return round(max(0.0, 1.0 - len(violations) * 0.25), 4)


def efficiency_score(
    steps_taken: int,
    max_steps_expected: int,
    max_steps_allowed: int = 15,
) -> float:
    """
    Score how efficiently the agent worked.
    Full score if steps_taken <= max_steps_expected.
    Linear decay to 0.0 as steps approach max_steps_allowed.
    """
    if steps_taken <= max_steps_expected:
        return 1.0
    over         = steps_taken - max_steps_expected
    allowed_over = max_steps_allowed - max_steps_expected
    if allowed_over <= 0:
        return 0.0
    return round(max(0.0, 1.0 - over / allowed_over), 4)


def compute_step_reward(
    action_type: str,
    action_value: str,
    task: Dict[str, Any],
    tools_used_so_far: List[str],
    violations_so_far: List[str],
) -> float:
    """
    Per-step partial reward — fires on every single action.
    This keeps the reward signal dense so the agent learns faster.
    Returns float in [-0.30, 0.15].

    Positive signals:
      +0.08  first time using a required tool
      +0.12  correctly flagging security when required
      +0.10  correctly escalating when required
      +0.03  asking a meaningful question or sending a response

    Negative signals:
      -0.20  refunding before security review on fraud task
      -0.15  refunding a serial abuser
    """
    reward = 0.0
    gt             = task["ground_truth"]
    required_tools = gt.get("required_tools", [])
    trap           = gt.get("trap", "")

    # Reward first use of each required tool
    if action_type in required_tools and action_type not in tools_used_so_far:
        reward += 0.08

    # Reward correctly identifying security issue
    if gt.get("should_flag_security") and action_type == "flag_security":
        reward += 0.12

    # Reward correct escalation
    if gt.get("should_escalate") and action_type == "escalate":
        reward += 0.10

    # Penalise falling into the refund trap on fraud tasks
    if "must_NOT_process_refund_before_security_review" in trap:
        if action_type == "process_refund":
            reward -= 0.20

    # Penalise refunding a serial abuser
    if "must_NOT_process_refund_no_valid_reason" in trap:
        if action_type == "process_refund":
            reward -= 0.15

    # Small reward for meaningful communication
    if action_type in ("ask_user", "send_response") and len(action_value) > 15:
        reward += 0.03

    return round(max(-0.30, min(0.15, reward)), 4)


def compute_episode_reward(
    resolved: bool,
    resolution_type_used: str,
    task: Dict[str, Any],
    tools_used: List[str],
    violations: List[str],
    steps_taken: int,
    did_escalate: bool,
    did_flag_security: bool,
    conversation_history: List[Dict],
) -> float:
    """
    Final episode reward — called once when done=True.
    Weighted sum of all component scores, clamped to [0.0, 1.0].
    Hard trap penalties applied on top of weighted sum.
    """
    gt = task["ground_truth"]

    # Find resolution keywords anywhere in the conversation
    all_text = " ".join(
        m.get("content", "").lower()
        for m in conversation_history
    )
    kw_found = [
        kw for kw in gt.get("correct_resolution_keywords", [])
        if kw.lower() in all_text
    ]

    r = resolution_score(
        resolved=resolved,
        resolution_type_used=resolution_type_used,
        ground_truth_resolution=gt.get("resolution_type", ""),
        kw_found=kw_found,
        required_escalation=gt.get("should_escalate", False),
        did_escalate=did_escalate,
        required_security_flag=gt.get("should_flag_security", False),
        did_flag_security=did_flag_security,
    )
    t = tool_use_score(tools_used, gt.get("required_tools", []))
    p = policy_score(violations)
    e = efficiency_score(steps_taken, gt.get("max_steps_expected", 8))

    final = (
        r * WEIGHTS["resolution"] +
        t * WEIGHTS["tool_use"]   +
        p * WEIGHTS["policy"]     +
        e * WEIGHTS["efficiency"]
    )

    # Hard penalties applied after weighted sum
    trap = gt.get("trap", "")
    if "must_NOT_process_refund" in trap and "process_refund" in tools_used:
        final -= 0.30
    if gt.get("should_flag_security") and "flag_security" not in tools_used:
        final -= 0.35

    return round(max(0.0, min(1.0, final)), 4)