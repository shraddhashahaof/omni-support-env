# # # server/tools.py
# # """
# # Tool implementations for OmniSupportEnv.
# # Each function simulates a real support tool an agent can call.
# # All responses are deterministic — same input always returns same output.
# # This ensures graders are reproducible across runs.

# # Available tools:
# #   search_knowledge_base  — search internal KB for policies
# #   lookup_order           — get order details by order ID
# #   check_account          — get account status and risk flags
# #   process_refund         — issue a refund
# #   flag_security          — raise a security alert on an account
# #   escalate_ticket        — escalate to specialist team
# #   ask_user               — send a clarifying question to the user
# #   send_response          — send a message to the user
# #   execute_tool           — router: maps action_type string to correct function
# # """
# # import sys
# # import os
# # sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # from typing import Any, Dict
# # from tasks import get_tool_response


# # def search_knowledge_base(query: str) -> Dict[str, Any]:
# #     """Search the internal knowledge base for policies and procedures."""
# #     result = get_tool_response("search_kb", query)
# #     return {
# #         "tool": "search_kb",
# #         "query": query,
# #         "result": result["data"],
# #         "found": result["found"],
# #     }


# # def lookup_order(order_id: str) -> Dict[str, Any]:
# #     """Fetch order details. Strips leading # from order IDs."""
# #     clean = order_id.strip().lstrip("#")
# #     result = get_tool_response("lookup_order", clean)
# #     return {
# #         "tool": "lookup_order",
# #         "order_id": order_id,
# #         "result": result["data"],
# #         "found": result["found"],
# #     }


# # def check_account(user_id: str) -> Dict[str, Any]:
# #     """
# #     Fetch account status, risk flags, and history.
# #     Agents MUST call this before processing any refund.
# #     """
# #     result = get_tool_response("check_account", user_id.strip())
# #     return {
# #         "tool": "check_account",
# #         "user_id": user_id,
# #         "result": result["data"],
# #         "found": result["found"],
# #     }


# # def process_refund(order_id: str, amount: str = "0", reason: str = "") -> Dict[str, Any]:
# #     """
# #     Issue a refund for an order.
# #     Params (all strings, comma-separated from action_value):
# #       order_id — the order to refund
# #       amount   — refund amount as string (e.g. "49.99")
# #       reason   — reason for the refund
# #     """
# #     try:
# #         amt = float(amount)
# #     except ValueError:
# #         amt = 0.0
# #     return {
# #         "tool": "process_refund",
# #         "order_id": order_id,
# #         "amount": amt,
# #         "reason": reason,
# #         "status": "processed",
# #         "confirmation_id": f"REF-{order_id}-{int(amt * 100)}",
# #         "message": (
# #             f"Refund of ${amt:.2f} for order {order_id} initiated. "
# #             "ETA 3-5 business days."
# #         ),
# #     }


# # def flag_security(user_id: str, reason: str = "unspecified") -> Dict[str, Any]:
# #     """
# #     Raise a security alert on an account.
# #     This is MANDATORY for fraud/suspicious activity cases.
# #     Missing this on fraud tasks causes severe penalty in grading.
# #     """
# #     return {
# #         "tool": "flag_security",
# #         "user_id": user_id,
# #         "reason": reason,
# #         "status": "flagged",
# #         "ticket_id": f"SEC-{user_id[-4:]}",
# #         "message": f"Security alert raised for {user_id}. Fraud team notified.",
# #     }


# # def escalate_ticket(reason: str, priority: str = "normal") -> Dict[str, Any]:
# #     """
# #     Escalate ticket to specialist team.
# #     Required for: chargebacks, fraud, enterprise P1, bulk operations, GDPR.
# #     """
# #     return {
# #         "tool": "escalate",
# #         "reason": reason,
# #         "priority": priority,
# #         "status": "escalated",
# #         "assigned_to": "specialist_team",
# #         "message": f"Escalated as {priority}. Specialist team notified.",
# #     }


# # def ask_user(question: str) -> Dict[str, Any]:
# #     """Send a clarifying question to the customer."""
# #     return {
# #         "tool": "ask_user",
# #         "question": question,
# #         "status": "sent",
# #         # Simulated user reply for testing purposes
# #         "simulated_reply": "Thank you for asking. Let me provide more details.",
# #     }


# # def send_response(message: str) -> Dict[str, Any]:
# #     """Send a message to the customer."""
# #     return {
# #         "tool": "send_response",
# #         "message": message,
# #         "status": "sent",
# #     }


# # def execute_tool(action_type: str, action_value: str) -> Dict[str, Any]:
# #     """
# #     Route an action_type string to the correct tool function.
# #     action_value format per tool:
# #       search_kb       — free text query
# #       lookup_order    — order ID (e.g. "78234" or "#78234")
# #       check_account   — user ID (e.g. "USR_4821")
# #       process_refund  — "order_id, amount, reason" (comma separated)
# #       flag_security   — "user_id, reason" (comma separated)
# #       escalate        — "reason" or "reason, priority"
# #       ask_user        — question text
# #       send_response   — message text
# #     """
# #     v = action_value.strip()
# #     try:
# #         if action_type == "search_kb":
# #             return search_knowledge_base(v)

# #         elif action_type == "lookup_order":
# #             return lookup_order(v)

# #         elif action_type == "check_account":
# #             return check_account(v)

# #         elif action_type == "process_refund":
# #             # Parse "order_id, amount, reason"
# #             parts = [p.strip() for p in v.split(",", 2)]
# #             return process_refund(*parts)

# #         elif action_type == "flag_security":
# #             # Parse "user_id, reason"
# #             parts = [p.strip() for p in v.split(",", 1)]
# #             return flag_security(*parts) if len(parts) >= 2 else flag_security(v)

# #         elif action_type == "escalate":
# #             # Parse "reason" or "reason, priority"
# #             parts = [p.strip() for p in v.split(",", 1)]
# #             return escalate_ticket(*parts) if len(parts) >= 2 else escalate_ticket(v)

# #         elif action_type == "ask_user":
# #             return ask_user(v)

# #         elif action_type == "send_response":
# #             return send_response(v)

# #         else:
# #             return {"tool": action_type, "status": "unknown_tool", "value": v}

# #     except Exception as e:
# #         return {"tool": action_type, "error": str(e), "status": "failed"}

# # server/tools.py

# import random
# import uuid
# from typing import Dict


# # =========================
# # MAIN TOOL EXECUTOR
# # =========================

# def execute_tool(
#     tool_name: str,
#     tool_input: str
# ) -> Dict:

#     if tool_name == "search_kb":
#         return _search_kb(tool_input)

#     if tool_name == "lookup_order":
#         return _lookup_order(tool_input)

#     if tool_name == "check_account":
#         return _check_account(tool_input)

#     if tool_name == "process_refund":
#         return _process_refund(tool_input)

#     if tool_name == "flag_security":
#         return _flag_security(tool_input)

#     if tool_name == "ask_user":
#         return _ask_user(tool_input)

#     if tool_name == "send_response":
#         return _send_response(tool_input)

#     if tool_name == "escalate":
#         return _escalate(tool_input)

#     return {
#         "success": False,
#         "message": "Unknown tool"
#     }


# # =========================
# # KNOWLEDGE BASE SEARCH
# # =========================

# def _search_kb(query: str):

#     responses = [

#         "Found KB article explaining refund timelines.",
#         "Password reset steps located.",
#         "Security verification process identified.",
#         "Order tracking instructions available.",
#         "Refund eligibility policy located."

#     ]

#     return {
#         "success": True,
#         "kb_id": f"KB-{random.randint(100,999)}",
#         "message": random.choice(responses),
#         "query": query
#     }


# # =========================
# # ORDER LOOKUP
# # =========================

# def _lookup_order(order_id: str):

#     status_options = [
#         "delivered",
#         "processing",
#         "cancelled",
#         "returned"
#     ]

#     return {
#         "success": True,
#         "order_id": order_id,
#         "status": random.choice(status_options),
#         "amount": round(random.uniform(10, 500), 2),
#         "currency": "USD"
#     }


# # =========================
# # ACCOUNT CHECK
# # =========================

# def _check_account(user_id: str):

#     tiers = [
#         "basic",
#         "premium",
#         "vip"
#     ]

#     return {
#         "success": True,
#         "user_id": user_id,
#         "account_status": "active",
#         "tier": random.choice(tiers),
#         "age_days": random.randint(10, 1500)
#     }


# # =========================
# # REFUND PROCESS
# # =========================

# def _process_refund(order_id: str):

#     refund_id = str(uuid.uuid4())[:8]

#     return {
#         "success": True,
#         "refund_id": refund_id,
#         "order_id": order_id,
#         "status": "initiated",
#         "eta_days": random.randint(3, 7)
#     }


# # =========================
# # SECURITY FLAG
# # =========================

# def _flag_security(reason: str):

#     case_id = f"SEC-{random.randint(1000,9999)}"

#     return {
#         "success": True,
#         "case_id": case_id,
#         "priority": "high",
#         "reason": reason
#     }


# # =========================
# # ASK USER
# # =========================

# def _ask_user(question: str):

#     return {
#         "success": True,
#         "question": question,
#         "message": "User clarification requested."
#     }


# # =========================
# # SEND RESPONSE
# # =========================

# def _send_response(message: str):

#     return {
#         "success": True,
#         "message": message,
#         "delivery": "sent"
#     }


# # =========================
# # ESCALATION
# # =========================

# def _escalate(reason: str):

#     escalation_id = f"ESC-{random.randint(1000,9999)}"

#     return {
#         "success": True,
#         "escalation_id": escalation_id,
#         "department": "Tier-2 Support",
#         "reason": reason
#     }

# server/tools.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict
from tasks import get_tool_response


def search_knowledge_base(query: str) -> Dict[str, Any]:
    result = get_tool_response("search_kb", query)
    return {"tool": "search_kb", "query": query, "result": result["data"], "found": result["found"]}


def lookup_order(order_id: str) -> Dict[str, Any]:
    clean = order_id.strip().lstrip("#")
    result = get_tool_response("lookup_order", clean)
    return {"tool": "lookup_order", "order_id": order_id, "result": result["data"], "found": result["found"]}


def check_account(user_id: str) -> Dict[str, Any]:
    result = get_tool_response("check_account", user_id.strip())
    return {"tool": "check_account", "user_id": user_id, "result": result["data"], "found": result["found"]}


def process_refund(order_id: str, amount: str = "0", reason: str = "") -> Dict[str, Any]:
    try:
        amt = float(amount)
    except ValueError:
        amt = 0.0
    return {
        "tool": "process_refund",
        "order_id": order_id,
        "amount": amt,
        "reason": reason,
        "status": "processed",
        "confirmation_id": f"REF-{order_id}-{int(amt*100)}",
        "message": f"Refund of ${amt:.2f} for order {order_id} initiated. ETA 3-5 business days.",
    }


def flag_security(user_id: str, reason: str = "unspecified") -> Dict[str, Any]:
    return {
        "tool": "flag_security",
        "user_id": user_id,
        "reason": reason,
        "status": "flagged",
        "ticket_id": f"SEC-{user_id[-4:]}",
        "message": f"Security alert raised for {user_id}. Fraud team notified.",
    }


def escalate_ticket(reason: str, priority: str = "normal") -> Dict[str, Any]:
    return {
        "tool": "escalate",
        "reason": reason,
        "priority": priority,
        "status": "escalated",
        "assigned_to": "specialist_team",
        "message": f"Escalated as {priority}. Specialist team notified.",
    }


def ask_user(question: str) -> Dict[str, Any]:
    return {"tool": "ask_user", "question": question, "status": "sent",
            "simulated_reply": "Thank you for asking. Let me provide more details."}


def send_response(message: str) -> Dict[str, Any]:
    return {"tool": "send_response", "message": message, "status": "sent"}


def execute_tool(action_type: str, action_value: str) -> Dict[str, Any]:
    v = action_value.strip()
    try:
        if action_type == "search_kb":       return search_knowledge_base(v)
        elif action_type == "lookup_order":  return lookup_order(v)
        elif action_type == "check_account": return check_account(v)
        elif action_type == "process_refund":
            parts = [p.strip() for p in v.split(",", 2)]
            return process_refund(*parts)
        elif action_type == "flag_security":
            parts = [p.strip() for p in v.split(",", 1)]
            return flag_security(*parts) if len(parts) >= 2 else flag_security(v)
        elif action_type == "escalate":
            parts = [p.strip() for p in v.split(",", 1)]
            return escalate_ticket(*parts) if len(parts) >= 2 else escalate_ticket(v)
        elif action_type == "ask_user":      return ask_user(v)
        elif action_type == "send_response": return send_response(v)
        else: return {"tool": action_type, "status": "unknown_tool", "value": v}
    except Exception as e:
        return {"tool": action_type, "error": str(e), "status": "failed"}