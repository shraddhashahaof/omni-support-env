# # agents.py — Multi-Agent System for OmniSupportEnv (Branch 7)
# #
# # Architecture:
# #   TriageAgent   — reads the ticket, classifies it, decides which specialist to use
# #   SpecialistAgent — executes tools, generates real LLM customer responses
# #
# # Dynamic responses: every send_response and ask_user message is generated
# # by the LLM in context — not a static string. The agent reads tool results
# # and crafts a real reply.
# #
# # Usage:
# #   python agents.py                         # all 15 tasks
# #   python agents.py hard_fraud_001          # specific task
# #   python agents.py --model Qwen/Qwen2.5-72B-Instruct hard_fraud_001

# import json, os, sys, time, argparse
# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

# API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
# MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
# HF_TOKEN     = os.getenv("HF_TOKEN")
# MAX_STEPS    = 12
# TEMPERATURE  = 0.3   # slightly higher than before — allows natural language variety
# SUCCESS_THRESHOLD = 0.5

# TASK_IDS = [
#     "easy_refund_001", "easy_password_001", "easy_cancel_001",
#     "easy_delivery_001", "easy_update_001",
#     "med_chargeback_001", "med_partial_refund_001", "med_tech_billing_001",
#     "med_subscription_dispute_001", "med_api_quota_001",
#     "hard_fraud_001", "hard_abuse_001", "hard_enterprise_breach_001",
#     "hard_bulk_001", "hard_gdpr_001",
# ]

# # ── ANSI colours ──────────────────────────────────────────────────────────────
# def _c(code, t): return f"\033[{code}m{t}\033[0m"
# def green(t):  return _c("32", t)
# def red(t):    return _c("31", t)
# def yellow(t): return _c("33", t)
# def cyan(t):   return _c("36", t)
# def bold(t):   return _c("1",  t)
# def dim(t):    return _c("2",  t)
# def magenta(t): return _c("35", t)


# # ══════════════════════════════════════════════════════════════════════════════
# # TRIAGE AGENT
# # Reads the ticket → classifies category → decides which specialist handles it
# # Returns structured JSON only — no customer-facing messages
# # ══════════════════════════════════════════════════════════════════════════════

# TRIAGE_SYSTEM = """You are a support triage agent. Read the customer ticket and classify it.

# Output ONLY valid JSON — no explanation, no markdown:
# {
#   "category": "<one of: billing, fraud, gdpr, enterprise, delivery, account, cancellation, abuse>",
#   "specialist": "<one of: billing_specialist, security_specialist, compliance_specialist, account_specialist>",
#   "urgency": "<P1 or P2>",
#   "summary": "<one sentence: what the customer needs>",
#   "risk_signals": ["<list any fraud/risk signals you see in the ticket>"],
#   "first_action": "<the very first tool call the specialist should make>"
# }

# Routing rules:
# - fraud signals / new account / high value claim / unauthorized → security_specialist
# - GDPR / data deletion / legal request → compliance_specialist
# - enterprise / API / quota / SLA / production down → billing_specialist with P1
# - chargeback / bulk refund / reseller → billing_specialist
# - password / login / account update / delivery / cancel → account_specialist
# - 4+ refunds / abuse pattern → security_specialist"""


# def triage(client, ticket, user_id, account_tier, account_age_days):
#     prompt = f"""Ticket: {ticket}
# User ID: {user_id} | Tier: {account_tier} | Age: {account_age_days} days

# Classify and route this ticket."""

#     try:
#         resp = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": TRIAGE_SYSTEM},
#                 {"role": "user",   "content": prompt},
#             ],
#             temperature=0.1,  # triage should be deterministic
#             max_tokens=300,
#         )
#         text = resp.choices[0].message.content or ""
#         text = text.strip()
#         if "```" in text:
#             text = "\n".join(l for l in text.splitlines() if not l.startswith("```")).strip()
#         s, e = text.find("{"), text.rfind("}") + 1
#         if s != -1 and e > s:
#             return json.loads(text[s:e])
#     except Exception as ex:
#         print(red(f"  [TRIAGE ERROR] {ex}"))
#     # fallback
#     return {
#         "category": "billing", "specialist": "billing_specialist",
#         "urgency": "P2", "summary": "Customer needs support",
#         "risk_signals": [], "first_action": "check_account"
#     }


# # ══════════════════════════════════════════════════════════════════════════════
# # SPECIALIST AGENT
# # Receives triage output + ticket → executes tools → generates REAL LLM responses
# # send_response and ask_user content is dynamically written by the LLM
# # ══════════════════════════════════════════════════════════════════════════════

# SPECIALIST_SYSTEM = """You are a {specialist_role} at a customer support center.

# TICKET SUMMARY (from triage): {summary}
# CATEGORY: {category} | URGENCY: {urgency}
# RISK SIGNALS: {risk_signals}

# AVAILABLE ACTIONS (output exactly one per turn as valid JSON):
# - search_kb       : search policy docs — value = keyword
# - lookup_order    : get order details — value = order ID from ticket
# - check_account   : get account info — value = user_id shown in context
# - process_refund  : issue refund — value = "order_id, amount, reason"
# - flag_security   : raise fraud alert — value = "user_id, reason"
# - ask_user        : ask customer for more info — value = YOUR ACTUAL QUESTION (write a real question)
# - send_response   : message to customer — value = YOUR ACTUAL RESPONSE (write a real, helpful message)
# - escalate        : escalate to specialist — value = "reason, priority"
# - resolve         : close ticket when done — value = brief resolution summary
# - close_no_action : close without action — value = reason

# MANDATORY POLICIES:
# 1. ALWAYS call check_account BEFORE process_refund
# 2. NEVER refund during active chargeback — escalate first
# 3. NEVER refund fraud/suspicious new accounts — flag_security + escalate
# 4. GDPR requests must be escalated, never closed
# 5. Refund abuse flag = decline and explain policy

# IMPORTANT FOR send_response and ask_user:
#   Write a REAL, professional, empathetic message to the customer.
#   Use the tool results you have seen. Be specific — mention order numbers,
#   amounts, timelines. Do NOT use placeholder text.

# DECISION FLOWCHART:
# - Duplicate charge? → lookup_order → check_account → process_refund → send_response(explain refund) → resolve
# - Password issue?  → check_account → search_kb → send_response(give reset steps) → resolve
# - Cancel request?  → check_account → search_kb → send_response(confirm cancellation + policy) → resolve
# - Late delivery?   → lookup_order → send_response(give tracking info) → resolve
# - Chargeback?      → lookup_order → check_account → search_kb → escalate → send_response(we're investigating) → resolve
# - Fraud signals?   → check_account → flag_security → escalate → send_response(account secured message) → resolve
# - Abuse pattern?   → check_account → search_kb → send_response(decline with policy reason) → resolve
# - Enterprise/P1?   → check_account → search_kb → escalate(P1) → send_response(SLA acknowledgement) → resolve
# - GDPR request?    → check_account → flag_security → search_kb → escalate → send_response(GDPR acknowledgement) → resolve

# RULES:
# - Never repeat an action with the same value
# - Call resolve AS SOON AS the required actions are complete (don't over-investigate)
# - Max {max_steps} steps

# Respond ONLY with valid JSON:
# {{"action_type": "<action>", "action_value": "<value>"}}"""


# def get_specialist_action(client, specialist_role, category, urgency, summary,
#                            risk_signals, conversation_history, max_steps):
#     system = SPECIALIST_SYSTEM.format(
#         specialist_role=specialist_role,
#         summary=summary,
#         category=category,
#         urgency=urgency,
#         risk_signals=", ".join(risk_signals) if risk_signals else "none",
#         max_steps=max_steps,
#     )

#     messages = [{"role": "system", "content": system}] + conversation_history

#     try:
#         resp = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=messages,
#             temperature=TEMPERATURE,
#             max_tokens=400,
#         )
#         text = resp.choices[0].message.content or ""
#         text = text.strip()
#         if "```" in text:
#             text = "\n".join(l for l in text.splitlines() if not l.startswith("```")).strip()
#         s, e = text.find("{"), text.rfind("}") + 1
#         if s != -1 and e > s:
#             data = json.loads(text[s:e])
#             return str(data.get("action_type", "resolve")), str(data.get("action_value", "done"))
#     except Exception as ex:
#         print(red(f"  [SPECIALIST ERROR] {ex}"))
#     return "resolve", "error"


# # ══════════════════════════════════════════════════════════════════════════════
# # EPISODE RUNNER
# # ══════════════════════════════════════════════════════════════════════════════

# def run_task(env_client, llm_client, task_id, index, total):
#     from models import SupportAction, ActionType

#     t0 = time.time()
#     step_rewards = []
#     final_score  = 0.0
#     steps_taken  = 0

#     # ── Reset environment ─────────────────────────────────────────────────────
#     raw = env_client.reset(task_id=task_id)
#     obs = raw  # LocalEnvClient returns obs directly

#     ticket    = getattr(obs, "ticket_text",        "")
#     user_id   = getattr(obs, "user_id",            "")
#     tier      = getattr(obs, "account_tier",       "free")
#     age       = getattr(obs, "account_age_days",    0)

#     diff_key = task_id.split("_")[0]
#     colour = {"easy": green, "med": yellow, "hard": red}.get(diff_key, cyan)
#     label  = {"easy": "EASY  ", "med": "MEDIUM", "hard": "HARD  "}.get(diff_key, "      ")

#     print()
#     print(colour(f"━━━  {label}  {task_id}  ━━━"))
#     print(f"  {dim('Ticket :')} {cyan(ticket[:140])}")
#     print(f"  {dim('Account:')} tier={tier}  age={age}d")
#     print()

#     # ── STEP 1: TRIAGE ────────────────────────────────────────────────────────
#     print(f"  {magenta('🔍 [TRIAGE AGENT]')} Classifying ticket...")
#     triage_result = triage(llm_client, ticket, user_id, tier, age)
#     specialist    = triage_result.get("specialist", "billing_specialist")
#     category      = triage_result.get("category",   "billing")
#     urgency       = triage_result.get("urgency",    "P2")
#     summary       = triage_result.get("summary",    ticket[:80])
#     risk_signals  = triage_result.get("risk_signals", [])
#     first_action  = triage_result.get("first_action", "check_account")

#     specialist_display = {
#         "billing_specialist":    "💳 Billing Specialist",
#         "security_specialist":   "🔒 Security Specialist",
#         "compliance_specialist": "⚖️  Compliance Specialist",
#         "account_specialist":    "👤 Account Specialist",
#     }.get(specialist, specialist)

#     print(f"  {magenta('→')} Routed to: {bold(specialist_display)}")
#     print(f"  {magenta('→')} Category: {category}  |  Urgency: {urgency}")
#     if risk_signals:
#         print(f"  {magenta('→')} Risk signals: {red(', '.join(risk_signals))}")
#     print(f"  {magenta('→')} Summary: {summary}")
#     print()

#     print(f"[START] task={task_id} specialist={specialist} urgency={urgency}", flush=True)

#     # ── Build conversation history for specialist ─────────────────────────────
#     # The specialist sees: ticket + account context + triage briefing
#     conversation_history = [
#         {
#             "role": "user",
#             "content": (
#                 f"=== CUSTOMER TICKET ===\n{ticket}\n\n"
#                 f"=== ACCOUNT CONTEXT ===\n"
#                 f"user_id      : {user_id}\n"
#                 f"account_tier : {tier}\n"
#                 f"account_age  : {age} days\n\n"
#                 f"=== TRIAGE BRIEFING ===\n"
#                 f"Triage classified this as: {category} | {urgency}\n"
#                 f"Summary: {summary}\n"
#                 f"Risk signals: {', '.join(risk_signals) if risk_signals else 'none'}\n"
#                 f"Suggested first action: {first_action}\n\n"
#                 f"Now handle this ticket. Start with {first_action}.\n"
#                 f"Next action (JSON only):"
#             )
#         }
#     ]

#     done = False

#     # ── STEP 2: SPECIALIST EXECUTES ───────────────────────────────────────────
#     for step in range(1, MAX_STEPS + 1):
#         if done:
#             break

#         print(f"  {dim(f'[{specialist_display}]')} Step {step}", end="  ")

#         atype_str, avalue = get_specialist_action(
#             llm_client, specialist, category, urgency, summary,
#             risk_signals, conversation_history, MAX_STEPS
#         )

#         print(f"{bold(atype_str):<22} val={cyan(avalue[:70])}")

#         # For send_response and ask_user, show the full message
#         if atype_str in ("send_response", "ask_user") and len(avalue) > 5:
#             prefix = "  📤 Response to customer:" if atype_str == "send_response" else "  ❓ Question to customer:"
#             print(f"{prefix}")
#             # Word-wrap the message for readability
#             words = avalue.split()
#             line, lines = [], []
#             for word in words:
#                 if len(" ".join(line + [word])) > 90:
#                     lines.append("     " + " ".join(line))
#                     line = [word]
#                 else:
#                     line.append(word)
#             if line:
#                 lines.append("     " + " ".join(line))
#             print("\n".join(lines))

#         # Execute in environment
#         try:
#             atype_enum = ActionType(atype_str)
#         except ValueError:
#             atype_enum = ActionType.RESOLVE

#         action = SupportAction(action_type=atype_enum, action_value=avalue)
#         result_obs = env_client.step(action)

#         reward   = getattr(result_obs, "reward", 0.0) or 0.0
#         done     = getattr(result_obs, "done",   False)
#         feedback = getattr(result_obs, "last_feedback", "")
#         viols    = getattr(result_obs, "policy_violations", [])
#         steps_taken = step

#         r_col = green(f"+{reward:.3f}") if reward > 0 else (red(f"{reward:.3f}") if reward < 0 else dim(f"{reward:.3f}"))
#         print(f"         reward={r_col}  done={str(done).lower()}")

#         # Show tool result feedback (not for resolve/close)
#         if feedback and "New ticket" not in feedback and atype_str not in ("resolve", "close_no_action"):
#             print(f"         {dim('→')} {feedback[:200]}")

#         if viols:
#             for v in viols:
#                 print(f"         {red(f'⚠ VIOLATION: {v}')}")

#         if done:
#             final_score = max(0.0, min(1.0, reward))
#         else:
#             step_rewards.append(reward)

#         print(f"[STEP] step={step} action={atype_str}:{avalue[:40]} reward={reward:.3f} done={str(done).lower()}", flush=True)

#         # Update conversation history for next specialist turn
#         # Add what the specialist did and what the environment returned
#         conversation_history.append({
#             "role": "assistant",
#             "content": json.dumps({"action_type": atype_str, "action_value": avalue})
#         })
#         if feedback and atype_str not in ("resolve", "close_no_action"):
#             conversation_history.append({
#                 "role": "user",
#                 "content": (
#                     f"Tool result: {feedback}\n"
#                     f"Cumulative reward so far: {getattr(result_obs, 'cumulative_reward', 0.0):.3f}\n"
#                     f"Steps remaining: {getattr(result_obs, 'steps_remaining', MAX_STEPS - step)}\n"
#                     + (f"\nWARNING — Policy violations: {'; '.join(viols)}" if viols else "")
#                     + "\nNext action (JSON only):"
#                 )
#             })

#         if done:
#             break

#     elapsed = time.time() - t0
#     success = final_score >= SUCCESS_THRESHOLD
#     status  = green("PASS") if success else red("FAIL")
#     bar_n   = int(final_score * 20)
#     bar     = green("█" * bar_n) + dim("░" * (20 - bar_n))

#     print()
#     print(f"  Result: {status}  score={bold(f'{final_score:.4f}')}  [{bar}]")
#     print(f"  Steps: {steps_taken}/{MAX_STEPS}   Time: {elapsed:.1f}s   Specialist: {specialist_display}")
#     if step_rewards:
#         print(f"  Step rewards: {', '.join(f'{r:.3f}' for r in step_rewards)}")
#     print()
#     rewards_str = ",".join(f"{r:.2f}" for r in step_rewards)
#     print(f"[END] task={task_id} success={str(success).lower()} steps={steps_taken} score={final_score:.4f} specialist={specialist} rewards=[{rewards_str}]", flush=True)

#     return final_score


# # ══════════════════════════════════════════════════════════════════════════════
# # LOCAL ENV CLIENT
# # ══════════════════════════════════════════════════════════════════════════════

# class LocalEnvClient:
#     def __init__(self):
#         server_dir = os.path.join(os.path.dirname(__file__), "server")
#         if server_dir not in sys.path:
#             sys.path.insert(0, server_dir)
#         from environment import OmniSupportEnvironment
#         self._env = OmniSupportEnvironment()

#     def reset(self, task_id=None):
#         return self._env.reset(task_id=task_id)

#     def step(self, action):
#         return self._env.step(action)

#     def close(self): pass


# # ══════════════════════════════════════════════════════════════════════════════
# # SUMMARY
# # ══════════════════════════════════════════════════════════════════════════════

# def print_summary(scores, task_ids, elapsed_total):
#     print("\n" + "=" * 66)
#     print("              MULTI-AGENT FINAL SUMMARY")
#     print("=" * 66)

#     groups = {"easy": [], "med": [], "hard": []}
#     for tid, sc in zip(task_ids, scores):
#         groups.setdefault(tid.split("_")[0], []).append(sc)

#     for label, key in [("Easy   (5)", "easy"), ("Medium (5)", "med"), ("Hard   (5)", "hard")]:
#         grp = groups.get(key, [])
#         if not grp:
#             continue
#         avg    = sum(grp) / len(grp)
#         passed = sum(1 for s in grp if s >= SUCCESS_THRESHOLD)
#         bar    = "█" * int(avg * 20) + "░" * (20 - int(avg * 20))
#         print(f"  {label}:  avg={avg:.4f}  [{bar}]  pass={passed}/{len(grp)}")

#     overall    = sum(scores) / len(scores) if scores else 0.0
#     total_pass = sum(1 for s in scores if s >= SUCCESS_THRESHOLD)
#     print(f"\n  Overall avg  : {bold(f'{overall:.4f}')}")
#     print(f"  Tasks passed : {total_pass}/{len(scores)}   Time: {elapsed_total:.1f}s\n")

#     print(dim("  Task                              Score    Status"))
#     print(dim("  " + "-" * 48))
#     for tid, sc in zip(task_ids, scores):
#         status = green("PASS") if sc >= SUCCESS_THRESHOLD else red("FAIL")
#         colour = {"easy": green, "med": yellow, "hard": red}.get(tid.split("_")[0], cyan)
#         print(f"  {colour(tid):<36} {sc:.4f}   {status}")

#     print()
#     avg_by_diff = {k: (sum(v)/len(v) if v else 0.0) for k, v in groups.items()}
#     parts = [f"tasks={len(task_ids)}", f"avg_score={overall:.4f}", f"passed={total_pass}/{len(scores)}"]
#     for k in ("easy", "med", "hard"):
#         if groups.get(k):
#             parts.append(f"{k}_avg={avg_by_diff[k]:.4f}")
#     print(f"[MULTI_AGENT_SUMMARY] {' '.join(parts)}", flush=True)


# # ══════════════════════════════════════════════════════════════════════════════
# # MAIN
# # ══════════════════════════════════════════════════════════════════════════════

# def main():
#     global MODEL_NAME
#     p = argparse.ArgumentParser(description="OmniSupportEnv Multi-Agent Runner")
#     p.add_argument("tasks",   nargs="*", help="task IDs (default: all 15)")
#     p.add_argument("--model", default=None, help="override MODEL_NAME")
#     args = p.parse_args()

#     if args.model:
#         MODEL_NAME = args.model

#     print()
#     print("=" * 66)
#     print("      OmniSupportEnv — Multi-Agent Evaluation (Branch 7)")
#     print("=" * 66)
#     print(f"  Model     : {MODEL_NAME}")
#     print(f"  Mode      : LOCAL (TriageAgent + SpecialistAgent)")
#     print(f"  Tasks     : {len(args.tasks or TASK_IDS)} tickets")
#     print(f"  Max steps : {MAX_STEPS}")
#     print()

#     env_client = LocalEnvClient()
#     llm_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")

#     tasks   = args.tasks if args.tasks else TASK_IDS
#     scores  = []
#     run_ids = []
#     t_start = time.time()

#     try:
#         for i, task_id in enumerate(tasks, 1):
#             score = run_task(env_client, llm_client, task_id, i, len(tasks))
#             scores.append(score)
#             run_ids.append(task_id)
#             if i < len(tasks):
#                 time.sleep(0.5)
#     finally:
#         env_client.close()

#     print_summary(scores, run_ids, time.time() - t_start)


# if __name__ == "__main__":
#     main()

# agent.py — Multi-Agent System for OmniSupportEnv (Branch 7)
#
# Architecture:
#   TriageAgent     — reads the ticket, classifies it, decides which specialist to use
#   SpecialistAgent — executes tools, generates real LLM customer responses
#
# Dynamic responses: every send_response and ask_user message is generated
# by the LLM in context — not a static string.
#
# Usage:
#   python agent.py                         # all 15 tasks
#   python agent.py hard_fraud_001          # specific task
#   python agent.py --model Qwen/Qwen2.5-72B-Instruct hard_fraud_001

import argparse
import json
import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
MAX_STEPS = 12
TEMPERATURE = 0.3
SUCCESS_THRESHOLD = 0.5

TASK_IDS = [
    "easy_refund_001", "easy_password_001", "easy_cancel_001",
    "easy_delivery_001", "easy_update_001",
    "med_chargeback_001", "med_partial_refund_001", "med_tech_billing_001",
    "med_subscription_dispute_001", "med_api_quota_001",
    "hard_fraud_001", "hard_abuse_001", "hard_enterprise_breach_001",
    "hard_bulk_001", "hard_gdpr_001",
]


# ══════════════════════════════════════════════════════════════════════════════
# ANSI COLOURS + FORMATTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _c(code, text):
    return f"\033[{code}m{text}\033[0m"


def green(text):
    return _c("32", text)


def red(text):
    return _c("31", text)


def yellow(text):
    return _c("33", text)


def cyan(text):
    return _c("36", text)


def bold(text):
    return _c("1", text)


def dim(text):
    return _c("2", text)


def magenta(text):
    return _c("35", text)


def safe_str(value, fallback=""):
    if value is None:
        return fallback
    return str(value)


def normalize_feedback(feedback):
    feedback = safe_str(feedback).strip()
    if not feedback or "New ticket" in feedback:
        return "No feedback"
    return feedback


def wrap_text(text, width=88, indent="      "):
    text = safe_str(text)
    words = text.split()
    if not words:
        return indent + ""

    lines = []
    line = []

    for word in words:
        candidate = " ".join(line + [word])
        if len(candidate) > width and line:
            lines.append(indent + " ".join(line))
            line = [word]
        else:
            line.append(word)

    if line:
        lines.append(indent + " ".join(line))

    return "\n".join(lines)


def tool_name(action_type):
    return {
        "search_kb": "Knowledge Base Search",
        "lookup_order": "Order Lookup",
        "check_account": "Account Verification",
        "process_refund": "Refund Processing",
        "flag_security": "Fraud / Security Alert",
        "ask_user": "Customer Clarification",
        "send_response": "Customer Messaging",
        "escalate": "Escalation",
        "resolve": "Ticket Resolution",
        "close_no_action": "No-Action Closure",
    }.get(action_type, "Unknown Tool")


def difficulty_label(task_id):
    key = task_id.split("_")[0]
    if key == "easy":
        return "EASY", green
    if key == "med":
        return "MEDIUM", yellow
    if key == "hard":
        return "HARD", red
    return key.upper(), cyan


def print_main_header(model_name, task_count):
    print()
    print(bold(cyan("=" * 150)))
    print(bold(cyan(" >>> OmniSupportEnv - Professional Multi-Agent Evaluation <<<")))
    print(bold(cyan("=" * 150)))
    print(f"Model     : {model_name}")
    print(f"Mode      : LOCAL Multi-Agent")
    print(f"Agents    : TriageAgent + SpecialistAgent")
    print(f"Tasks     : {task_count}")
    print(f"Max Steps : {MAX_STEPS}")
    print(bold("=" * 78))


def print_task_header(task_id, ticket, tier, age):
    label, colour = difficulty_label(task_id)
    print()
    print(colour(bold(f" [ TASK: {task_id} | Difficulty: {label.upper()} ] ")))
    print(colour("-" * 150))
    print(f"Ticket  : {ticket}")
    print(f"Account : tier={tier} | age={age}d")


def print_triage_result(category, urgency, specialist_display, risk_signals, summary, first_action):
    print()
    print(magenta(bold(" [ TRIAGE ANALYSIS ]")))
    print(magenta("-" * 150))
    print(f"Category     : {category}")
    print(f"Urgency      : {urgency}")
    print(f"Specialist   : {specialist_display}")
    print(f"Risk Signals : {', '.join(risk_signals) if risk_signals else 'none'}")
    print(f"Summary      : {summary}")
    print(f"First Action : {first_action}")


def print_step_output(step, specialist_display, action, value, reward, done, feedback="", violations=None):
    violations = violations or []
    feedback = normalize_feedback(feedback)

    reward_text = green(f"+{reward:.3f}") if reward > 0 else red(f"{reward:.3f}") if reward < 0 else dim(f"{reward:.3f}")
    done_text = green("true") if done else yellow("false")

    print()
    print(yellow(bold(f" [ STEP {step} ]")))
    print(yellow("-" * 150))
    print(f"Agent   : {specialist_display}")
    print(f"Action  : {bold(action)}")
    print(f"Value   : {cyan(value)}")
    print(f"Tool    : {tool_name(action)}")
    print(f"Result  : {feedback}")

    if action in ("send_response", "ask_user"):
        label = "Agent Response" if action == "send_response" else "Agent Question"
        print()
        print(cyan(bold(label)))
        print(wrap_text(value))
        print()
        print(green(bold("Customer Received")))
        print(wrap_text(value))

    if violations:
        print()
        print(red(bold("Policy Violations")))
        for violation in violations:
            print(f"      - {violation}")

    print(f"Reward  : {reward_text} | Done: {done_text}")


def print_task_result(task_id, success, final_score, steps_taken, elapsed, specialist_display, step_rewards):
    status = green("PASS") if success else red("FAIL")
    bar_n = int(final_score * 20)
    bar = green("#" * bar_n) + dim("-" * (20 - bar_n))

    print()
    print(bold(green("=" * 150)))
    print(bold(green(" [ TASK RESULT SUMMARY ]")))
    print(bold(green("=" * 150)))
    print(f"Task         : {task_id}")
    print(f"Status       : {status}")
    print(f"Score        : {final_score:.4f}")
    print(f"Performance  : {bar}")
    print(f"Steps Used   : {steps_taken}/{MAX_STEPS}")
    print(f"Time         : {elapsed:.1f}s")
    print(f"Specialist   : {specialist_display}")
    print(f"Step Rewards : [{', '.join(f'{r:.3f}' for r in step_rewards)}]")
    print(bold(green("=" * 150)))


# ══════════════════════════════════════════════════════════════════════════════
# TRIAGE AGENT
# ══════════════════════════════════════════════════════════════════════════════

TRIAGE_SYSTEM = """You are a support triage agent. Read the customer ticket and classify it.

Output ONLY valid JSON — no explanation, no markdown:
{
  "category": "<one of: billing, fraud, gdpr, enterprise, delivery, account, cancellation, abuse>",
  "specialist": "<one of: billing_specialist, security_specialist, compliance_specialist, account_specialist>",
  "urgency": "<P1 or P2>",
  "summary": "<one sentence: what the customer needs>",
  "risk_signals": ["<list any fraud/risk signals you see in the ticket>"],
  "first_action": "<the very first tool call the specialist should make>"
}

Routing rules:
- fraud signals / new account / high value claim / unauthorized → security_specialist
- GDPR / data deletion / legal request → compliance_specialist
- enterprise / API / quota / SLA / production down → billing_specialist with P1
- chargeback / bulk refund / reseller → billing_specialist
- password / login / account update / delivery / cancel → account_specialist
- 4+ refunds / abuse pattern → security_specialist"""


def extract_json_object(text):
    text = safe_str(text).strip()
    if "```" in text:
        text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("```"))

    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        return json.loads(text[start:end])
    raise ValueError("No JSON object found in LLM response")


def triage(client, ticket, user_id, account_tier, account_age_days):
    prompt = f"""Ticket: {ticket}
User ID: {user_id} | Tier: {account_tier} | Age: {account_age_days} days

Classify and route this ticket."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=300,
        )
        text = response.choices[0].message.content or ""
        return extract_json_object(text)
    except Exception as ex:
        print(red(f"[TRIAGE ERROR] {ex}"))
        return {
            "category": "billing",
            "specialist": "billing_specialist",
            "urgency": "P2",
            "summary": "Customer needs support",
            "risk_signals": [],
            "first_action": "check_account",
        }


# ══════════════════════════════════════════════════════════════════════════════
# SPECIALIST AGENT
# ══════════════════════════════════════════════════════════════════════════════

SPECIALIST_SYSTEM = """You are a {specialist_role} at a customer support center.

TICKET SUMMARY (from triage): {summary}
CATEGORY: {category} | URGENCY: {urgency}
RISK SIGNALS: {risk_signals}

AVAILABLE ACTIONS (output exactly one per turn as valid JSON):
- search_kb       : search policy docs — value = keyword (e.g. 'refund')
- lookup_order    : get order details — value = the numeric ID (e.g. '78234')
- check_account   : get account info — value = the user ID (e.g. 'USR_1234')
- process_refund  : issue refund — value = "order_id, amount, reason"
- flag_security   : raise fraud alert — value = "user_id, reason"
- ask_user        : ask customer for more info — value = YOUR ACTUAL QUESTION
- send_response   : message to customer — value = YOUR ACTUAL RESPONSE
- escalate        : escalate to specialist — value = "reason, priority"
- resolve         : close ticket when done — value = brief resolution summary
- close_no_action : close without action — value = reason

MANDATORY POLICIES:
1. ALWAYS call check_account BEFORE process_refund
2. NEVER refund during active chargeback — escalate first
3. NEVER refund fraud/suspicious new accounts — flag_security + escalate
4. GDPR requests must be escalated, never closed
5. Refund abuse flag = decline and explain policy

IMPORTANT FOR send_response and ask_user:
Write a REAL, professional, empathetic message to the customer.
Use the tool results you have seen. Be specific — mention order numbers,
amounts, timelines. Do NOT use placeholder text.

DECISION FLOWCHART:
- Duplicate charge? → lookup_order → check_account → process_refund → send_response → resolve
- Password issue?  → check_account → search_kb → send_response → resolve
- Cancel request?  → check_account → send_response → resolve
- Late delivery?   → lookup_order → send_response → resolve
- Chargeback?      → lookup_order → check_account → escalate → send_response → resolve
- Fraud signals?   → check_account → flag_security → escalate → send_response → resolve
- Abuse pattern?   → check_account → lookup_order → search_kb → send_response → resolve
- Enterprise/P1?   → check_account → search_kb → escalate(P1) → send_response → resolve
- GDPR request?    → check_account → flag_security → search_kb → escalate → send_response → resolve
- Bulk/Reseller?   → check_account → escalate → send_response → resolve
- Partial Refund?  → lookup_order → check_account → process_refund → send_response → resolve
- Sub Dispute?     → check_account → lookup_order → process_refund → send_response → resolve

RULES:
- ONLY use the actions listed above. NEVER invent new tool names like 'check_api_key_activity'.
- Never repeat an action with the same value.
- Hit ALL mandatory tools mentioned in the flowchart for the specific issue.
- BULK/RESELLER requests (more than 1 account) MUST be escalated. NEVER process bulk refunds yourself.
- Call resolve AS SOON AS the required actions are complete (don't over-investigate).
- Max {max_steps} steps.

Respond ONLY with valid JSON:
{{"action_type": "<action>", "action_value": "<value>"}}"""


def get_specialist_action(
    client,
    specialist_role,
    category,
    urgency,
    summary,
    risk_signals,
    conversation_history,
    max_steps,
):
    system = SPECIALIST_SYSTEM.format(
        specialist_role=specialist_role,
        summary=summary,
        category=category,
        urgency=urgency,
        risk_signals=", ".join(risk_signals) if risk_signals else "none",
        max_steps=max_steps,
    )

    messages = [{"role": "system", "content": system}] + conversation_history

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=400,
        )
        text = response.choices[0].message.content or ""
        data = extract_json_object(text)
        return str(data.get("action_type", "resolve")), str(data.get("action_value", "done"))
    except Exception as ex:
        print(red(f"[SPECIALIST ERROR] {ex}"))
        return "resolve", "error"


# ══════════════════════════════════════════════════════════════════════════════
# LOCAL ENV CLIENT
# ══════════════════════════════════════════════════════════════════════════════

class LocalEnvClient:
    def __init__(self):
        server_dir = os.path.join(os.path.dirname(__file__), "server")
        if server_dir not in sys.path:
            sys.path.insert(0, server_dir)
        from environment import OmniSupportEnvironment
        self._env = OmniSupportEnvironment()

    def reset(self, task_id=None):
        return self._env.reset(task_id=task_id)

    def step(self, action):
        return self._env.step(action)

    def close(self):
        pass


# ══════════════════════════════════════════════════════════════════════════════
# EPISODE RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_task(env_client, llm_client, task_id, index, total):
    from models import SupportAction, ActionType

    start_time = time.time()
    step_rewards = []
    final_score = 0.0
    steps_taken = 0

    obs = env_client.reset(task_id=task_id)

    ticket = getattr(obs, "ticket_text", "")
    user_id = getattr(obs, "user_id", "")
    tier = getattr(obs, "account_tier", "free")
    age = getattr(obs, "account_age_days", 0)

    print_task_header(task_id, ticket, tier, age)

    triage_result = triage(llm_client, ticket, user_id, tier, age)
    specialist = triage_result.get("specialist", "billing_specialist")
    category = triage_result.get("category", "billing")
    urgency = triage_result.get("urgency", "P2")
    summary = triage_result.get("summary", ticket[:80])
    risk_signals = triage_result.get("risk_signals", [])
    first_action = triage_result.get("first_action", "check_account")

    specialist_display = {
        "billing_specialist": "Billing Specialist",
        "security_specialist": "Security Specialist",
        "compliance_specialist": "Compliance Specialist",
        "account_specialist": "Account Specialist",
    }.get(specialist, specialist)

    print_triage_result(category, urgency, specialist_display, risk_signals, summary, first_action)
    print(f"\n[START] task={task_id} specialist={specialist} urgency={urgency}", flush=True)

    conversation_history = [
        {
            "role": "user",
            "content": (
                f"=== CUSTOMER TICKET ===\n{ticket}\n\n"
                f"=== ACCOUNT CONTEXT ===\n"
                f"user_id      : {user_id}\n"
                f"account_tier : {tier}\n"
                f"account_age  : {age} days\n\n"
                f"=== TRIAGE BRIEFING ===\n"
                f"Triage classified this as: {category} | {urgency}\n"
                f"Summary: {summary}\n"
                f"Risk signals: {', '.join(risk_signals) if risk_signals else 'none'}\n"
                f"Suggested first action: {first_action}\n\n"
                f"Now handle this ticket. Start with {first_action}.\n"
                f"Next action (JSON only):"
            ),
        }
    ]

    done = False

    for step in range(1, MAX_STEPS + 1):
        if done:
            break

        action_type_str, action_value = get_specialist_action(
            llm_client,
            specialist,
            category,
            urgency,
            summary,
            risk_signals,
            conversation_history,
            MAX_STEPS,
        )

        try:
            action_type_enum = ActionType(action_type_str)
        except ValueError:
            action_type_enum = ActionType.RESOLVE

        action = SupportAction(action_type=action_type_enum, action_value=action_value)
        result_obs = env_client.step(action)

        reward = getattr(result_obs, "reward", 0.0) or 0.0
        done = getattr(result_obs, "done", False)
        feedback = getattr(result_obs, "last_feedback", "")
        violations = getattr(result_obs, "policy_violations", [])
        cumulative_reward = getattr(result_obs, "cumulative_reward", 0.0)
        steps_remaining = getattr(result_obs, "steps_remaining", MAX_STEPS - step)
        steps_taken = step

        print_step_output(
            step=step,
            specialist_display=specialist_display,
            action=action_type_str,
            value=action_value,
            reward=reward,
            done=done,
            feedback=feedback,
            violations=violations,
        )

        print(
            f"[STEP] step={step} action={action_type_str}:{action_value[:40]} "
            f"reward={reward:.3f} done={str(done).lower()}",
            flush=True,
        )

        if done:
            final_score = max(0.0, min(1.0, reward))
        else:
            step_rewards.append(reward)

        conversation_history.append(
            {
                "role": "assistant",
                "content": json.dumps({"action_type": action_type_str, "action_value": action_value}),
            }
        )

        if feedback and action_type_str not in ("resolve", "close_no_action"):
            conversation_history.append(
                {
                    "role": "user",
                    "content": (
                        f"Tool result: {feedback}\n"
                        f"Cumulative reward so far: {cumulative_reward:.3f}\n"
                        f"Steps remaining: {steps_remaining}\n"
                        + (f"\nWARNING — Policy violations: {'; '.join(violations)}" if violations else "")
                        + "\nNext action (JSON only):"
                    ),
                }
            )

        if done:
            break

    elapsed = time.time() - start_time
    success = final_score >= SUCCESS_THRESHOLD

    print_task_result(
        task_id=task_id,
        success=success,
        final_score=final_score,
        steps_taken=steps_taken,
        elapsed=elapsed,
        specialist_display=specialist_display,
        step_rewards=step_rewards,
    )

    rewards_str = ",".join(f"{r:.2f}" for r in step_rewards)
    print(
        f"[END] task={task_id} success={str(success).lower()} steps={steps_taken} "
        f"score={final_score:.4f} specialist={specialist} rewards=[{rewards_str}]",
        flush=True,
    )

    return final_score


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_summary(scores, task_ids, elapsed_total):
    print("\n" + bold(cyan("=" * 150)))
    print(bold(cyan(" [ MULTI-AGENT FINAL EVALUATION SUMMARY ]")))
    print(bold(cyan("=" * 150)))

    groups = {"easy": [], "med": [], "hard": []}
    for task_id, score in zip(task_ids, scores):
        groups.setdefault(task_id.split("_")[0], []).append(score)

    for label, key in [("Easy", "easy"), ("Medium", "med"), ("Hard", "hard")]:
        group_scores = groups.get(key, [])
        if not group_scores:
            continue

        avg_score = sum(group_scores) / len(group_scores)
        passed = sum(1 for score in group_scores if score >= SUCCESS_THRESHOLD)
        bar = green("#" * int(avg_score * 20)) + dim("-" * (20 - int(avg_score * 20)))
        print(f"{label:<8}: avg={avg_score:.4f} | pass={passed}/{len(group_scores)} | {bar}")

    overall = sum(scores) / len(scores) if scores else 0.0
    total_pass = sum(1 for score in scores if score >= SUCCESS_THRESHOLD)

    print("-" * 78)
    print(f"Overall Avg : {overall:.4f}")
    print(f"Tasks Passed: {total_pass}/{len(scores)}")
    print(f"Total Time  : {elapsed_total:.1f}s")

    print("\nTask Scores")
    print("-" * 78)
    print(f"{'Task':<34} {'Score':<10} {'Status'}")
    print("-" * 78)

    for task_id, score in zip(task_ids, scores):
        status = green("PASS") if score >= SUCCESS_THRESHOLD else red("FAIL")
        _, colour = difficulty_label(task_id)
        print(f"{colour(task_id):<43} {score:<10.4f} {status}")

    avg_by_diff = {key: (sum(values) / len(values) if values else 0.0) for key, values in groups.items()}
    parts = [f"tasks={len(task_ids)}", f"avg_score={overall:.4f}", f"passed={total_pass}/{len(scores)}"]
    for key in ("easy", "med", "hard"):
        if groups.get(key):
            parts.append(f"{key}_avg={avg_by_diff[key]:.4f}")

    print()
    print(f"[MULTI_AGENT_SUMMARY] {' '.join(parts)}", flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    global MODEL_NAME

    parser = argparse.ArgumentParser(description="OmniSupportEnv Multi-Agent Runner")
    parser.add_argument("tasks", nargs="*", help="task IDs (default: all 15)")
    parser.add_argument("--model", default=None, help="override MODEL_NAME")
    args = parser.parse_args()

    if args.model:
        MODEL_NAME = args.model

    tasks = args.tasks if args.tasks else TASK_IDS
    print_main_header(MODEL_NAME, len(tasks))

    env_client = LocalEnvClient()
    llm_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")

    scores = []
    run_ids = []
    start_time = time.time()

    try:
        for index, task_id in enumerate(tasks, 1):
            score = run_task(env_client, llm_client, task_id, index, len(tasks))
            scores.append(score)
            run_ids.append(task_id)
            if index < len(tasks):
                time.sleep(0.5)
    finally:
        env_client.close()

    print_summary(scores, run_ids, time.time() - start_time)


if __name__ == "__main__":
    main()