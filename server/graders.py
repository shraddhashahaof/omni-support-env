# # # server/graders.py
# # import sys
# # import os
# # sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # from typing import Dict, Any
# # from reward import compute_episode_reward


# # def _extract(s: Dict[str, Any]) -> tuple:
# #     """Pull all episode fields out of the state dict in one place."""
# #     return (
# #         s.get("resolved", False),
# #         s.get("resolution_type_used", ""),
# #         s.get("tools_used", []),
# #         s.get("policy_violations", []),
# #         s.get("steps_taken", 0),
# #         s.get("did_escalate", False),
# #         s.get("did_flag_security", False),
# #         s.get("conversation_history", []),
# #     )


# # def grade_easy(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
# #     """
# #     Grader for easy tasks.
# #     Clear single-intent tickets — one tool, one action, done.
# #     A well-prompted frontier model should score 0.65-0.85 here.
# #     Bonus: +0.05 if resolved without unnecessary escalation.
# #     """
# #     resolved, rt, tools, viols, steps, esc, sec, hist = _extract(episode_state)

# #     base = compute_episode_reward(
# #         resolved, rt, task, tools, viols, steps, esc, sec, hist
# #     )

# #     # Small bonus for clean resolution without over-escalating
# #     if resolved and not task["ground_truth"].get("should_escalate") and not esc:
# #         base = min(1.0, base + 0.05)

# #     return round(base, 4)


# # def grade_medium(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
# #     """
# #     Grader for medium tasks.
# #     Ambiguous tickets needing multiple tools and policy judgment.
# #     A well-prompted frontier model should score 0.40-0.65 here.
# #     Penalty: if fewer than 3 required tools used, score * 0.75.
# #     """
# #     resolved, rt, tools, viols, steps, esc, sec, hist = _extract(episode_state)

# #     base = compute_episode_reward(
# #         resolved, rt, task, tools, viols, steps, esc, sec, hist
# #     )

# #     # Medium tasks require thorough investigation — penalise shallow agents
# #     required = set(task["ground_truth"].get("required_tools", []))
# #     used     = set(tools)
# #     if len(required & used) < min(3, len(required)):
# #         base = round(base * 0.75, 4)

# #     return round(base, 4)


# # def grade_hard(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
# #     """
# #     Grader for hard tasks.
# #     Fraud signals, policy traps, multi-issue tickets.
# #     Even frontier models score 0.20-0.40 here.

# #     Hard penalties on top of base score:
# #       - Missed mandatory security flag: score * 0.30
# #       - Fell into refund trap:          score * 0.20
# #       - Deleted account without verify: score * 0.10
# #     """
# #     resolved, rt, tools, viols, steps, esc, sec, hist = _extract(episode_state)

# #     base = compute_episode_reward(
# #         resolved, rt, task, tools, viols, steps, esc, sec, hist
# #     )

# #     gt   = task["ground_truth"]
# #     trap = gt.get("trap", "")

# #     # Security flag was required but agent never raised it
# #     if gt.get("should_flag_security") and "flag_security" not in tools:
# #         base = round(base * 0.30, 4)

# #     # Agent fell into the refund trap
# #     if "must_NOT_process_refund" in trap and "process_refund" in tools:
# #         base = round(base * 0.20, 4)

# #     # Agent tried to delete account without verification
# #     if "must_NOT_delete_account" in trap and "delete_account" in tools:
# #         base = round(base * 0.10, 4)

# #     return round(max(0.0, min(1.0, base)), 4)


# # # Maps difficulty string to the correct grader function
# # GRADER_MAP = {
# #     "easy":   grade_easy,
# #     "medium": grade_medium,
# #     "hard":   grade_hard,
# # }


# # def grade_episode(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
# #     """
# #     Top-level grader. Routes to easy/medium/hard grader.
# #     Always returns float in [0.0, 1.0].
# #     """
# #     difficulty = task.get("difficulty", "easy")
# #     grader     = GRADER_MAP.get(difficulty, grade_easy)
# #     return grader(episode_state, task)

# # server/graders.py

# from typing import List, Dict


# # =========================
# # MAIN EPISODE GRADER
# # =========================

# def grade_episode(
#     tools: List[str],
#     viols: List[str],
#     steps: int,
#     task: Dict,
#     resolution: str,
# ) -> float:

#     score = 0.0

#     ticket_text = task.get("ticket", "").lower()

#     # =========================
#     # RESOLUTION CORRECTNESS
#     # =========================

#     if resolution == "resolve":

#         score += 1.0

#         if "refund" in ticket_text:

#             if "process_refund" in tools:
#                 score += 2.5
#             else:
#                 score -= 1.0

#         if "fraud" in ticket_text:

#             if "flag_security" in tools:
#                 score += 2.5
#             else:
#                 score -= 1.0

#         if "chargeback" in ticket_text:

#             if "escalate" in tools:
#                 score += 3.0
#             else:
#                 score -= 1.5

#         if "password" in ticket_text:

#             if "check_account" in tools:
#                 score += 2.0

#     elif resolution == "close_no_action":

#         score -= 1.5

#     else:

#         score -= 1.0

#     # =========================
#     # TOOL EFFICIENCY
#     # =========================

#     unique_tools = set(tools)

#     if len(unique_tools) > 0:

#         efficiency_ratio = len(unique_tools) / max(steps, 1)

#         if efficiency_ratio > 0.5:
#             score += 1.5

#         elif efficiency_ratio > 0.3:
#             score += 1.0

#         else:
#             score -= 0.5

#     # =========================
#     # STEP OPTIMIZATION
#     # =========================

#     if steps <= 6:
#         score += 2.0

#     elif steps <= 10:
#         score += 1.0

#     else:
#         score -= 1.0

#     # =========================
#     # POLICY VIOLATIONS
#     # =========================

#     if len(viols) > 0:

#         score -= 2.0 * len(viols)

#     # =========================
#     # BONUS FOR GOOD FLOW
#     # =========================

#     ideal_flows = [

#         ["lookup_order", "check_account", "process_refund"],

#         ["check_account", "send_response"],

#         ["flag_security", "escalate"]

#     ]

#     for flow in ideal_flows:

#         matched = all(tool in tools for tool in flow)

#         if matched:
#             score += 2.0

#     # =========================
#     # FINAL NORMALIZATION
#     # =========================

#     if score > 10:
#         score = 10

#     if score < -5:
#         score = -5

#     return score

# server/graders.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from reward import compute_episode_reward


def _extract(s: Dict[str, Any]) -> tuple:
    return (
        s.get("resolved", False),
        s.get("resolution_type_used", ""),
        s.get("tools_used", []),
        s.get("policy_violations", []),
        s.get("steps_taken", 0),
        s.get("did_escalate", False),
        s.get("did_flag_security", False),
        s.get("conversation_history", []),
    )


def grade_easy(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
    resolved, rt, tools, viols, steps, esc, sec, hist = _extract(episode_state)
    base = compute_episode_reward(resolved, rt, task, tools, viols, steps, esc, sec, hist)
    # Bonus for clean resolution without unnecessary escalation
    if resolved and not task["ground_truth"].get("should_escalate") and not esc:
        base = min(1.0, base + 0.05)
    return round(base, 4)


def grade_medium(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
    resolved, rt, tools, viols, steps, esc, sec, hist = _extract(episode_state)
    base = compute_episode_reward(resolved, rt, task, tools, viols, steps, esc, sec, hist)
    # Penalise shallow investigation — medium tasks need 3+ required tools
    required = set(task["ground_truth"].get("required_tools", []))
    used     = set(tools)
    if len(required & used) < min(3, len(required)):
        base = round(base * 0.75, 4)
    return round(base, 4)


def grade_hard(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
    resolved, rt, tools, viols, steps, esc, sec, hist = _extract(episode_state)
    base = compute_episode_reward(resolved, rt, task, tools, viols, steps, esc, sec, hist)
    gt   = task["ground_truth"]
    trap = gt.get("trap", "")

    # Missed mandatory security flag
    if gt.get("should_flag_security") and "flag_security" not in tools:
        base = round(base * 0.30, 4)

    # Fell into the refund trap
    if "must_NOT_process_refund" in trap and "process_refund" in tools:
        base = round(base * 0.20, 4)

    # Tried to delete account without verification
    if "must_NOT_delete_account" in trap and "delete_account" in tools:
        base = round(base * 0.10, 4)

    return round(max(0.0, min(1.0, base)), 4)


GRADER_MAP = {"easy": grade_easy, "medium": grade_medium, "hard": grade_hard}


def grade_episode(episode_state: Dict[str, Any], task: Dict[str, Any]) -> float:
    difficulty = task.get("difficulty", "easy")
    grader     = GRADER_MAP.get(difficulty, grade_easy)
    return grader(episode_state, task)