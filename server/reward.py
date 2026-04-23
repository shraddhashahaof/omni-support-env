# server/reward.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any

WEIGHTS = {"resolution": 0.40, "tool_use": 0.25, "policy": 0.20, "efficiency": 0.15}


def resolution_score(resolved, resolution_type_used, ground_truth_resolution,
                     kw_found, required_escalation, did_escalate,
                     required_security_flag, did_flag_security) -> float:
    if not resolved:
        return 0.0
    score = 0.0
    gt_words   = set(ground_truth_resolution.replace("_", " ").split())
    used_words = set(resolution_type_used.replace("_", " ").split())
    score += min(0.50, len(gt_words & used_words) * 0.12)
    score += min(0.25, len(kw_found) * 0.05)
    score += (0.15 if did_escalate else -0.20) if required_escalation else 0.05
    score += (0.15 if did_flag_security else -0.30) if required_security_flag else 0.05
    return round(max(0.0, min(1.0, score)), 4)


def tool_use_score(tools_used, required_tools) -> float:
    if not required_tools:
        return 1.0
    required = set(required_tools)
    used     = set(tools_used)
    if not used:
        return 0.0
    coverage  = len(required & used) / len(required)
    extra     = max(0, len(used - required) - 1)
    precision = max(0.0, 1.0 - extra * 0.10)
    return round(coverage * 0.65 + precision * 0.35, 4)


def policy_score(violations) -> float:
    if not violations:
        return 1.0
    return round(max(0.0, 1.0 - len(violations) * 0.25), 4)


def efficiency_score(steps_taken, max_steps_expected, max_steps_allowed=15) -> float:
    if steps_taken <= max_steps_expected:
        return 1.0
    over         = steps_taken - max_steps_expected
    allowed_over = max_steps_allowed - max_steps_expected
    if allowed_over <= 0:
        return 0.0
    return round(max(0.0, 1.0 - over / allowed_over), 4)


def compute_step_reward(action_type, action_value, task, tools_used_so_far, violations_so_far) -> float:
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
    if "must_NOT_process_refund_before_security_review" in trap and action_type == "process_refund":
        reward -= 0.20

    # Penalise refunding a serial abuser
    if "must_NOT_process_refund_no_valid_reason" in trap and action_type == "process_refund":
        reward -= 0.15

    # Small reward for meaningful communication
    if action_type in ("ask_user", "send_response") and len(action_value) > 15:
        reward += 0.03

    return round(max(-0.30, min(0.15, reward)), 4)


def compute_episode_reward(resolved, resolution_type_used, task, tools_used,
                           violations, steps_taken, did_escalate,
                           did_flag_security, conversation_history) -> float:
    gt = task["ground_truth"]
    all_text = " ".join(m.get("content", "").lower() for m in conversation_history)
    kw_found = [kw for kw in gt.get("correct_resolution_keywords", []) if kw.lower() in all_text]

    r = resolution_score(resolved, resolution_type_used,
                         gt.get("resolution_type", ""), kw_found,
                         gt.get("should_escalate", False), did_escalate,
                         gt.get("should_flag_security", False), did_flag_security)
    t = tool_use_score(tools_used, gt.get("required_tools", []))
    p = policy_score(violations)
    e = efficiency_score(steps_taken, gt.get("max_steps_expected", 8))

    final = (r * WEIGHTS["resolution"] + t * WEIGHTS["tool_use"] +
             p * WEIGHTS["policy"]     + e * WEIGHTS["efficiency"])

    # Hard trap penalties
    trap = gt.get("trap", "")
    if "must_NOT_process_refund" in trap and "process_refund" in tools_used:
        final -= 0.30
    if gt.get("should_flag_security") and "flag_security" not in tools_used:
        final -= 0.35

    return round(max(0.0, min(1.0, final)), 4)