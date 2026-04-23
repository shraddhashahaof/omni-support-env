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