# # server/tasks.py
# """
# Task definitions for OmniSupportEnv.
# Each task is a hand-crafted support ticket with:
#   - ticket: the customer message the agent sees
#   - ground_truth: what a correct agent should do (used by graders)
#   - difficulty: easy / medium / hard
# 15 tasks total: 5 per difficulty level.
# """
# from typing import Dict, Any, List

# TASKS: List[Dict[str, Any]] = [

#     # ──────────────────────────────────────────────────────────
#     # EASY TASKS (5)
#     # Clear single-intent tickets. 1-2 tools needed.
#     # A good agent should score 0.65-0.85 on these.
#     # ──────────────────────────────────────────────────────────
#     {
#         "id": "easy_refund_001",
#         "difficulty": "easy",
#         "ticket": "I was charged twice for order #78234 last Tuesday. I want my money back.",
#         "user_id": "USR_4821",
#         "account_tier": "premium",
#         "account_age_days": 420,
#         "ground_truth": {
#             "resolution_type": "refund",
#             "required_tools": ["lookup_order", "process_refund"],
#             "correct_resolution_keywords": ["refund", "duplicate", "charged twice"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 6,
#         },
#     },
#     {
#         "id": "easy_password_001",
#         "difficulty": "easy",
#         "ticket": "I can't log into my account. I keep getting invalid password error.",
#         "user_id": "USR_1193",
#         "account_tier": "free",
#         "account_age_days": 90,
#         "ground_truth": {
#             "resolution_type": "account_unlock",
#             "required_tools": ["check_account", "search_kb"],
#             "correct_resolution_keywords": ["password reset", "reset link"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 5,
#         },
#     },
#     {
#         "id": "easy_cancel_001",
#         "difficulty": "easy",
#         "ticket": "Please cancel my subscription. I don't want to be charged next month.",
#         "user_id": "USR_3311",
#         "account_tier": "premium",
#         "account_age_days": 200,
#         "ground_truth": {
#             "resolution_type": "cancellation",
#             "required_tools": ["check_account"],
#             "correct_resolution_keywords": ["cancel", "subscription", "confirm"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 4,
#         },
#     },
#     {
#         "id": "easy_delivery_001",
#         "difficulty": "easy",
#         "ticket": "My order #90221 was supposed to arrive 3 days ago. Where is it?",
#         "user_id": "USR_7712",
#         "account_tier": "free",
#         "account_age_days": 60,
#         "ground_truth": {
#             "resolution_type": "provide_tracking",
#             "required_tools": ["lookup_order"],
#             "correct_resolution_keywords": ["tracking", "delayed", "carrier"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 4,
#         },
#     },
#     {
#         "id": "easy_update_001",
#         "difficulty": "easy",
#         "ticket": "I need to update my billing address. I moved to a new city.",
#         "user_id": "USR_5544",
#         "account_tier": "free",
#         "account_age_days": 150,
#         "ground_truth": {
#             "resolution_type": "guide_self_service",
#             "required_tools": ["search_kb"],
#             "correct_resolution_keywords": ["billing address", "account settings"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 3,
#         },
#     },

#     # ──────────────────────────────────────────────────────────
#     # MEDIUM TASKS (5)
#     # Ambiguous intent, multiple tools needed, policy judgment required.
#     # A good agent should score 0.40-0.65 on these.
#     # ──────────────────────────────────────────────────────────
#     {
#         "id": "med_chargeback_001",
#         "difficulty": "medium",
#         "ticket": (
#             "I never received order #66112 but tracking says delivered. "
#             "I want a refund AND I am filing a chargeback with my bank."
#         ),
#         "user_id": "USR_2209",
#         "account_tier": "premium",
#         "account_age_days": 800,
#         "ground_truth": {
#             "resolution_type": "investigate_then_refund",
#             "required_tools": ["lookup_order", "check_account", "process_refund"],
#             "correct_resolution_keywords": ["investigate", "carrier", "chargeback"],
#             # Agent MUST escalate when chargeback is mentioned — policy requirement
#             "should_escalate": True,
#             "should_flag_security": False,
#             "max_steps_expected": 8,
#             "policy_check": "chargeback_prevention_policy",
#         },
#     },
#     {
#         "id": "med_partial_refund_001",
#         "difficulty": "medium",
#         "ticket": "The product I received is damaged but I want to keep it. Can I get a partial refund?",
#         "user_id": "USR_8831",
#         "account_tier": "free",
#         "account_age_days": 30,
#         "ground_truth": {
#             "resolution_type": "partial_refund_after_verification",
#             "required_tools": ["lookup_order", "check_account", "search_kb"],
#             "correct_resolution_keywords": ["partial", "damaged", "photo", "verify"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 8,
#         },
#     },
#     {
#         "id": "med_tech_billing_001",
#         "difficulty": "medium",
#         "ticket": (
#             "Your app keeps crashing and I was charged for premium features "
#             "I cannot even use. This is unacceptable."
#         ),
#         "user_id": "USR_4401",
#         "account_tier": "premium",
#         "account_age_days": 350,
#         "ground_truth": {
#             "resolution_type": "tech_support_then_credit",
#             "required_tools": ["search_kb", "check_account", "process_refund"],
#             "correct_resolution_keywords": ["crash", "credit", "technical"],
#             "should_escalate": True,
#             "should_flag_security": False,
#             "max_steps_expected": 9,
#         },
#     },
#     {
#         "id": "med_subscription_dispute_001",
#         "difficulty": "medium",
#         "ticket": (
#             "I cancelled my subscription 2 months ago but you are still charging me. "
#             "I want ALL my money back for the last 2 months."
#         ),
#         "user_id": "USR_6622",
#         "account_tier": "premium",
#         "account_age_days": 500,
#         "ground_truth": {
#             "resolution_type": "verify_cancellation_then_refund",
#             "required_tools": ["check_account", "lookup_order", "process_refund"],
#             "correct_resolution_keywords": ["verify", "cancellation", "refund"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "max_steps_expected": 8,
#         },
#     },
#     {
#         "id": "med_api_quota_001",
#         "difficulty": "medium",
#         "ticket": (
#             "Our API quota was exceeded and our production system went down. "
#             "We are on enterprise plan but got no warning."
#         ),
#         "user_id": "USR_ENT_001",
#         "account_tier": "enterprise",
#         "account_age_days": 1200,
#         "ground_truth": {
#             "resolution_type": "escalate_with_interim_fix",
#             "required_tools": ["check_account", "search_kb", "escalate"],
#             "correct_resolution_keywords": ["quota", "escalate", "enterprise"],
#             "should_escalate": True,
#             "should_flag_security": False,
#             "max_steps_expected": 7,
#         },
#     },

#     # ──────────────────────────────────────────────────────────
#     # HARD TASKS (5)
#     # Fraud signals, policy conflicts, traps for naive agents.
#     # Even frontier models score 0.20-0.40 on these.
#     # ──────────────────────────────────────────────────────────
#     {
#         "id": "hard_fraud_001",
#         "difficulty": "hard",
#         "ticket": (
#             "There are 3 transactions on my account I did not make. "
#             "All happened last night. Total is $847. I need refunds immediately."
#         ),
#         "user_id": "USR_9901",
#         "account_tier": "premium",
#         "account_age_days": 25,   # NEW account — major fraud signal
#         "ground_truth": {
#             "resolution_type": "flag_fraud_escalate_do_not_refund_yet",
#             "required_tools": ["check_account", "flag_security", "escalate"],
#             "correct_resolution_keywords": ["fraud", "security", "verify", "freeze"],
#             "should_escalate": True,
#             "should_flag_security": True,   # MANDATORY — missing this = severe penalty
#             "max_steps_expected": 8,
#             # Trap: naive agent will immediately process refund — wrong!
#             "trap": "agent_must_NOT_process_refund_before_security_review",
#         },
#     },
#     {
#         "id": "hard_abuse_001",
#         "difficulty": "hard",
#         "ticket": (
#             "I want a refund on this order. Also on the previous 3 orders last month. "
#             "The products were fine but I just do not want them anymore."
#         ),
#         "user_id": "USR_7733",
#         "account_tier": "free",
#         "account_age_days": 45,
#         "ground_truth": {
#             "resolution_type": "decline_serial_refund_policy_cite",
#             "required_tools": ["check_account", "lookup_order", "search_kb"],
#             "correct_resolution_keywords": ["policy", "decline", "previous refunds"],
#             "should_escalate": False,
#             "should_flag_security": False,
#             "refund_should_be_denied": True,
#             "max_steps_expected": 7,
#             # Trap: agent must NOT just process refund — account has abuse flag
#             "trap": "agent_must_NOT_process_refund_no_valid_reason",
#         },
#     },
#     {
#         "id": "hard_enterprise_breach_001",
#         "difficulty": "hard",
#         "ticket": (
#             "We think our API key was compromised. We see calls from IPs in 3 countries. "
#             "We need key rotation, 30-day audit log, and security incident report."
#         ),
#         "user_id": "USR_ENT_002",
#         "account_tier": "enterprise",
#         "account_age_days": 900,
#         "ground_truth": {
#             "resolution_type": "security_incident_full_response",
#             "required_tools": ["check_account", "flag_security", "search_kb", "escalate"],
#             "correct_resolution_keywords": ["key rotation", "audit", "incident", "escalate"],
#             "should_escalate": True,
#             "should_flag_security": True,
#             "max_steps_expected": 10,
#         },
#     },
#     {
#         "id": "hard_bulk_001",
#         "difficulty": "hard",
#         "ticket": (
#             "I am a reseller with 12 accounts all having the same billing issue. "
#             "I need bulk refunds for all accounts TODAY or I will post on Twitter."
#         ),
#         "user_id": "USR_RESELLER_001",
#         "account_tier": "premium",
#         "account_age_days": 600,
#         "ground_truth": {
#             "resolution_type": "escalate_bulk_cannot_process_individually",
#             "required_tools": ["check_account", "search_kb", "escalate"],
#             "correct_resolution_keywords": ["escalate", "bulk", "account manager"],
#             "should_escalate": True,
#             "should_flag_security": False,
#             "max_steps_expected": 7,
#             # Trap: agent must NOT try to process 12 individual refunds
#             "trap": "agent_must_NOT_process_12_individual_refunds",
#         },
#     },
#     {
#         "id": "hard_gdpr_001",
#         "difficulty": "hard",
#         "ticket": (
#             "Under GDPR I am requesting all data you hold about me. "
#             "Also delete everything. Also I want a refund for last year. "
#             "My account has also been hacked."
#         ),
#         "user_id": "USR_3388",
#         "account_tier": "free",
#         "account_age_days": 730,
#         "ground_truth": {
#             "resolution_type": "triage_into_separate_tickets",
#             "required_tools": ["check_account", "flag_security", "search_kb", "escalate"],
#             "correct_resolution_keywords": ["GDPR", "separate", "security", "escalate"],
#             "should_escalate": True,
#             "should_flag_security": True,
#             "max_steps_expected": 10,
#             # Trap: agent must NOT delete account without identity verification
#             "trap": "agent_must_NOT_delete_account_without_verification",
#         },
#     },
# ]

# # ──────────────────────────────────────────────────────────────
# # Deterministic tool response data.
# # These are the fixed responses tools return for known inputs.
# # Keeping them hardcoded ensures graders are fully reproducible.
# # ──────────────────────────────────────────────────────────────
# TOOL_RESPONSES = {
#     "lookup_order": {
#         "78234": {
#             "status": "delivered",
#             "amount": 49.99,
#             "duplicate_charge": True,
#             "date": "2024-01-10",
#         },
#         "90221": {
#             "status": "in_transit",
#             "carrier": "BlueDart",
#             "eta": "2024-01-14",
#             "tracking": "BD992211",
#         },
#         "66112": {
#             "status": "delivered",
#             "proof_of_delivery": "signature_collected",
#             "address": "123 Main St",
#         },
#     },
#     "check_account": {
#         "USR_4821": {
#             "status": "active",
#             "refunds_this_month": 0,
#             "tier": "premium",
#             "flags": [],
#         },
#         "USR_9901": {
#             # High risk: new account + high value dispute
#             "status": "active",
#             "tier": "premium",
#             "flags": ["new_account", "high_value_dispute"],
#             "risk_score": 0.87,
#         },
#         "USR_7733": {
#             # Refund abuser: 4 refunds in 90 days
#             "status": "active",
#             "tier": "free",
#             "flags": ["refund_abuse_flag"],
#             "refund_count_90_days": 4,
#         },
#         "USR_ENT_001": {
#             "status": "active",
#             "tier": "enterprise",
#             "quota_usage": "101%",
#             "flags": ["quota_exceeded"],
#         },
#         "USR_ENT_002": {
#             # Compromised API key signals
#             "status": "active",
#             "tier": "enterprise",
#             "flags": ["suspicious_api_activity"],
#             "anomaly_score": 0.92,
#         },
#     },
#     "search_kb": {
#         "refund": (
#             "Refund policy: eligible within 30 days of purchase. "
#             "Max 2 refunds per 90 days per account. Use process_refund tool."
#         ),
#         "password": (
#             "Account access: reset at /account/reset. "
#             "Accounts lock after 5 failed attempts for 24 hours."
#         ),
#         "cancel": (
#             "Cancellation: immediate effect. "
#             "Pro-rata refund applies. Confirmation sent via email."
#         ),
#         "chargeback": (
#             "Chargeback policy: Escalate to billing specialist immediately. "
#             "Do NOT process refund while chargeback is pending."
#         ),
#         "fraud": (
#             "Fraud policy: Flag via flag_security tool, escalate immediately. "
#             "Do NOT process refunds. Freeze account pending review."
#         ),
#         "gdpr": (
#             "GDPR requests: Route to privacy@company.com. 30-day SLA. "
#             "Must verify identity before processing. Separate from other issues."
#         ),
#         "enterprise": (
#             "Enterprise SLA: P1 incidents escalate within 1 hour. "
#             "Account manager assigned. Use escalate tool with priority=P1."
#         ),
#         "damaged": (
#             "Damaged goods: Request photo evidence first. "
#             "Partial refunds up to 50% allowed. Full replacement requires return."
#         ),
#         "bulk": (
#             "Bulk operations: Must be processed by Account Management team. "
#             "Not possible via support portal. Use escalate tool."
#         ),
#         "quota": (
#             "API quota: Emergency increases require engineering approval. "
#             "Escalate as P1 for enterprise accounts."
#         ),
#         "abuse": (
#             "Refund abuse: More than 3 refunds in 90 days triggers abuse flag. "
#             "Decline and cite policy. Do not process further refunds."
#         ),
#     },
# }


# def get_task_by_id(task_id: str) -> dict:
#     """Fetch a task by its unique ID. Raises ValueError if not found."""
#     for t in TASKS:
#         if t["id"] == task_id:
#             return t
#     raise ValueError(f"Task {task_id!r} not found")


# def get_tasks_by_difficulty(difficulty: str) -> list:
#     """Return all tasks matching a given difficulty level."""
#     return [t for t in TASKS if t["difficulty"] == difficulty]


# def get_tool_response(tool: str, query: str) -> dict:
#     """
#     Look up a deterministic tool response.
#     Tries exact match first, then substring match.
#     Returns {"found": bool, "data": ...}
#     """
#     responses = TOOL_RESPONSES.get(tool, {})
#     # Exact match
#     if query in responses:
#         return {"found": True, "data": responses[query]}
#     # Substring match (e.g. "refund policy" matches key "refund")
#     for key, value in responses.items():
#         if key.lower() in query.lower():
#             return {"found": True, "data": value}
#     return {"found": False, "data": f"No results for '{query}'"}

# server/tasks.py
"""
Task definitions for OmniSupportEnv.
Each task is a hand-crafted support ticket with:
  - ticket: the customer message the agent sees
  - ground_truth: what a correct agent should do (used by graders)
  - difficulty: easy / medium / hard
15 tasks total: 5 per difficulty level.
"""
from typing import Dict, Any, List

TASKS: List[Dict[str, Any]] = [

    # ──────────────────────────────────────────────────────────
    # EASY TASKS (5)
    # Clear single-intent tickets. 1-2 tools needed.
    # A good agent should score 0.65-0.85 on these.
    # ──────────────────────────────────────────────────────────
    {
        "id": "easy_refund_001",
        "difficulty": "easy",
        "ticket": "I was charged twice for order #78234 last Tuesday. I want my money back.",
        "user_id": "USR_4821",
        "account_tier": "premium",
        "account_age_days": 420,
        "ground_truth": {
            "resolution_type": "refund",
            "required_tools": ["lookup_order", "process_refund"],
            "correct_resolution_keywords": ["refund", "duplicate", "charged twice"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 6,
        },
    },
    {
        "id": "easy_password_001",
        "difficulty": "easy",
        "ticket": "I can't log into my account. I keep getting invalid password error.",
        "user_id": "USR_1193",
        "account_tier": "free",
        "account_age_days": 90,
        "ground_truth": {
            "resolution_type": "account_unlock",
            "required_tools": ["check_account", "search_kb"],
            "correct_resolution_keywords": ["password reset", "reset link"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 5,
        },
    },
    {
        "id": "easy_cancel_001",
        "difficulty": "easy",
        "ticket": "Please cancel my subscription. I don't want to be charged next month.",
        "user_id": "USR_3311",
        "account_tier": "premium",
        "account_age_days": 200,
        "ground_truth": {
            "resolution_type": "cancellation",
            "required_tools": ["check_account"],
            "correct_resolution_keywords": ["cancel", "subscription", "confirm"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 4,
        },
    },
    {
        "id": "easy_delivery_001",
        "difficulty": "easy",
        "ticket": "My order #90221 was supposed to arrive 3 days ago. Where is it?",
        "user_id": "USR_7712",
        "account_tier": "free",
        "account_age_days": 60,
        "ground_truth": {
            "resolution_type": "provide_tracking",
            "required_tools": ["lookup_order"],
            "correct_resolution_keywords": ["tracking", "delayed", "carrier"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 4,
        },
    },
    {
        "id": "easy_update_001",
        "difficulty": "easy",
        "ticket": "I need to update my billing address. I moved to a new city.",
        "user_id": "USR_5544",
        "account_tier": "free",
        "account_age_days": 150,
        "ground_truth": {
            "resolution_type": "guide_self_service",
            "required_tools": ["search_kb"],
            "correct_resolution_keywords": ["billing address", "account settings"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 3,
        },
    },

    # ──────────────────────────────────────────────────────────
    # MEDIUM TASKS (5)
    # Ambiguous intent, multiple tools needed, policy judgment required.
    # A good agent should score 0.40-0.65 on these.
    # ──────────────────────────────────────────────────────────
    {
        "id": "med_chargeback_001",
        "difficulty": "medium",
        "ticket": (
            "I never received order #66112 but tracking says delivered. "
            "I want a refund AND I am filing a chargeback with my bank."
        ),
        "user_id": "USR_2209",
        "account_tier": "premium",
        "account_age_days": 800,
        "ground_truth": {
            "resolution_type": "investigate_then_refund",
            "required_tools": ["lookup_order", "check_account", "process_refund"],
            "correct_resolution_keywords": ["investigate", "carrier", "chargeback"],
            # Agent MUST escalate when chargeback is mentioned — policy requirement
            "should_escalate": True,
            "should_flag_security": False,
            "max_steps_expected": 8,
            "policy_check": "chargeback_prevention_policy",
        },
    },
    {
        "id": "med_partial_refund_001",
        "difficulty": "medium",
        "ticket": "The product I received is damaged but I want to keep it. Can I get a partial refund?",
        "user_id": "USR_8831",
        "account_tier": "free",
        "account_age_days": 30,
        "ground_truth": {
            "resolution_type": "partial_refund_after_verification",
            "required_tools": ["lookup_order", "check_account", "search_kb"],
            "correct_resolution_keywords": ["partial", "damaged", "photo", "verify"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 8,
        },
    },
    {
        "id": "med_tech_billing_001",
        "difficulty": "medium",
        "ticket": (
            "Your app keeps crashing and I was charged for premium features "
            "I cannot even use. This is unacceptable."
        ),
        "user_id": "USR_4401",
        "account_tier": "premium",
        "account_age_days": 350,
        "ground_truth": {
            "resolution_type": "tech_support_then_credit",
            "required_tools": ["search_kb", "check_account", "process_refund"],
            "correct_resolution_keywords": ["crash", "credit", "technical"],
            "should_escalate": True,
            "should_flag_security": False,
            "max_steps_expected": 9,
        },
    },
    {
        "id": "med_subscription_dispute_001",
        "difficulty": "medium",
        "ticket": (
            "I cancelled my subscription 2 months ago but you are still charging me. "
            "I want ALL my money back for the last 2 months."
        ),
        "user_id": "USR_6622",
        "account_tier": "premium",
        "account_age_days": 500,
        "ground_truth": {
            "resolution_type": "verify_cancellation_then_refund",
            "required_tools": ["check_account", "lookup_order", "process_refund"],
            "correct_resolution_keywords": ["verify", "cancellation", "refund"],
            "should_escalate": False,
            "should_flag_security": False,
            "max_steps_expected": 8,
        },
    },
    {
        "id": "med_api_quota_001",
        "difficulty": "medium",
        "ticket": (
            "Our API quota was exceeded and our production system went down. "
            "We are on enterprise plan but got no warning."
        ),
        "user_id": "USR_ENT_001",
        "account_tier": "enterprise",
        "account_age_days": 1200,
        "ground_truth": {
            "resolution_type": "escalate_with_interim_fix",
            "required_tools": ["check_account", "search_kb", "escalate"],
            "correct_resolution_keywords": ["quota", "escalate", "enterprise"],
            "should_escalate": True,
            "should_flag_security": False,
            "max_steps_expected": 7,
        },
    },

    # ──────────────────────────────────────────────────────────
    # HARD TASKS (5)
    # Fraud signals, policy conflicts, traps for naive agents.
    # Even frontier models score 0.20-0.40 on these.
    # ──────────────────────────────────────────────────────────
    {
        "id": "hard_fraud_001",
        "difficulty": "hard",
        "ticket": (
            "There are 3 transactions on my account I did not make. "
            "All happened last night. Total is $847. I need refunds immediately."
        ),
        "user_id": "USR_9901",
        "account_tier": "premium",
        "account_age_days": 25,   # NEW account — major fraud signal
        "ground_truth": {
            "resolution_type": "flag_fraud_escalate_do_not_refund_yet",
            "required_tools": ["check_account", "flag_security", "escalate"],
            "correct_resolution_keywords": ["fraud", "security", "verify", "freeze"],
            "should_escalate": True,
            "should_flag_security": True,   # MANDATORY — missing this = severe penalty
            "max_steps_expected": 8,
            # Trap: naive agent will immediately process refund — wrong!
            "trap": "agent_must_NOT_process_refund_before_security_review",
        },
    },
    {
        "id": "hard_abuse_001",
        "difficulty": "hard",
        "ticket": (
            "I want a refund on this order. Also on the previous 3 orders last month. "
            "The products were fine but I just do not want them anymore."
        ),
        "user_id": "USR_7733",
        "account_tier": "free",
        "account_age_days": 45,
        "ground_truth": {
            "resolution_type": "decline_serial_refund_policy_cite",
            "required_tools": ["check_account", "lookup_order", "search_kb"],
            "correct_resolution_keywords": ["policy", "decline", "previous refunds"],
            "should_escalate": False,
            "should_flag_security": False,
            "refund_should_be_denied": True,
            "max_steps_expected": 7,
            # Trap: agent must NOT just process refund — account has abuse flag
            "trap": "agent_must_NOT_process_refund_no_valid_reason",
        },
    },
    {
        "id": "hard_enterprise_breach_001",
        "difficulty": "hard",
        "ticket": (
            "We think our API key was compromised. We see calls from IPs in 3 countries. "
            "We need key rotation, 30-day audit log, and security incident report."
        ),
        "user_id": "USR_ENT_002",
        "account_tier": "enterprise",
        "account_age_days": 900,
        "ground_truth": {
            "resolution_type": "security_incident_full_response",
            "required_tools": ["check_account", "flag_security", "search_kb", "escalate"],
            "correct_resolution_keywords": ["key rotation", "audit", "incident", "escalate"],
            "should_escalate": True,
            "should_flag_security": True,
            "max_steps_expected": 10,
        },
    },
    {
        "id": "hard_bulk_001",
        "difficulty": "hard",
        "ticket": (
            "I am a reseller with 12 accounts all having the same billing issue. "
            "I need bulk refunds for all accounts TODAY or I will post on Twitter."
        ),
        "user_id": "USR_RESELLER_001",
        "account_tier": "premium",
        "account_age_days": 600,
        "ground_truth": {
            "resolution_type": "escalate_bulk_cannot_process_individually",
            "required_tools": ["check_account", "search_kb", "escalate"],
            "correct_resolution_keywords": ["escalate", "bulk", "account manager"],
            "should_escalate": True,
            "should_flag_security": False,
            "max_steps_expected": 7,
            # Trap: agent must NOT try to process 12 individual refunds
            "trap": "agent_must_NOT_process_12_individual_refunds",
        },
    },
    {
        "id": "hard_gdpr_001",
        "difficulty": "hard",
        "ticket": (
            "Under GDPR I am requesting all data you hold about me. "
            "Also delete everything. Also I want a refund for last year. "
            "My account has also been hacked."
        ),
        "user_id": "USR_3388",
        "account_tier": "free",
        "account_age_days": 730,
        "ground_truth": {
            "resolution_type": "triage_into_separate_tickets",
            "required_tools": ["check_account", "flag_security", "search_kb", "escalate"],
            "correct_resolution_keywords": ["GDPR", "separate", "security", "escalate"],
            "should_escalate": True,
            "should_flag_security": True,
            "max_steps_expected": 10,
            # Trap: agent must NOT delete account without identity verification
            "trap": "agent_must_NOT_delete_account_without_verification",
        },
    },
]

# ──────────────────────────────────────────────────────────────
# Deterministic tool response data.
# These are the fixed responses tools return for known inputs.
# Keeping them hardcoded ensures graders are fully reproducible.
# ──────────────────────────────────────────────────────────────
TOOL_RESPONSES = {
    "lookup_order": {
        "78234": {
            "status": "delivered",
            "amount": 49.99,
            "duplicate_charge": True,
            "date": "2024-01-10",
        },
        "90221": {
            "status": "in_transit",
            "carrier": "BlueDart",
            "eta": "2024-01-14",
            "tracking": "BD992211",
        },
        "66112": {
            "status": "delivered",
            "proof_of_delivery": "signature_collected",
            "address": "123 Main St",
        },
    },
    "check_account": {
        "USR_4821": {
            "status": "active",
            "refunds_this_month": 0,
            "tier": "premium",
            "flags": [],
        },
        "USR_9901": {
            # High risk: new account + high value dispute
            "status": "active",
            "tier": "premium",
            "flags": ["new_account", "high_value_dispute"],
            "risk_score": 0.87,
        },
        "USR_7733": {
            # Refund abuser: 4 refunds in 90 days
            "status": "active",
            "tier": "free",
            "flags": ["refund_abuse_flag"],
            "refund_count_90_days": 4,
        },
        "USR_ENT_001": {
            "status": "active",
            "tier": "enterprise",
            "quota_usage": "101%",
            "flags": ["quota_exceeded"],
        },
        "USR_ENT_002": {
            "status": "active",
            "tier": "enterprise",
            "flags": ["suspicious_api_activity"],
            "anomaly_score": 0.92,
        },
        # All remaining task accounts
        "USR_1193": {"status": "active", "tier": "free",    "flags": ["locked_account"],                    "refunds_this_month": 0},
        "USR_3311": {"status": "active", "tier": "premium", "flags": [],                                    "refunds_this_month": 0},
        "USR_7712": {"status": "active", "tier": "free",    "flags": [],                                    "refunds_this_month": 0},
        "USR_5544": {"status": "active", "tier": "free",    "flags": [],                                    "refunds_this_month": 0},
        "USR_2209": {"status": "active", "tier": "premium", "flags": [],                                    "refunds_this_month": 1},
        "USR_8831": {"status": "active", "tier": "free",    "flags": [],                                    "refunds_this_month": 0},
        "USR_4401": {"status": "active", "tier": "premium", "flags": ["billing_dispute"],                   "refunds_this_month": 0},
        "USR_6622": {"status": "active", "tier": "premium", "flags": ["subscription_active_after_cancel"],  "refunds_this_month": 2},
        "USR_RESELLER_001": {"status": "active", "tier": "premium", "flags": ["reseller_account"],          "linked_accounts": 12},
        "USR_3388": {"status": "active", "tier": "free",    "flags": ["gdpr_request_pending"],              "refunds_this_month": 0},
    },
    "search_kb": {
        "billing": (
            "Billing address: update via Account Settings > Billing. "
            "Changes take effect on next billing cycle."
        ),
        "refund": (
            "Refund policy: eligible within 30 days of purchase. "
            "Max 2 refunds per 90 days per account. Use process_refund tool."
        ),
        "password": (
            "Account access: reset at /account/reset. "
            "Accounts lock after 5 failed attempts for 24 hours."
        ),
        "cancel": (
            "Cancellation: immediate effect. "
            "Pro-rata refund applies. Confirmation sent via email."
        ),
        "chargeback": (
            "Chargeback policy: Escalate to billing specialist immediately. "
            "Do NOT process refund while chargeback is pending."
        ),
        "fraud": (
            "Fraud policy: Flag via flag_security tool, escalate immediately. "
            "Do NOT process refunds. Freeze account pending review."
        ),
        "gdpr": (
            "GDPR requests: Route to privacy@company.com. 30-day SLA. "
            "Must verify identity before processing. Separate from other issues."
        ),
        "enterprise": (
            "Enterprise SLA: P1 incidents escalate within 1 hour. "
            "Account manager assigned. Use escalate tool with priority=P1."
        ),
        "damaged": (
            "Damaged goods: Request photo evidence first. "
            "Partial refunds up to 50% allowed. Full replacement requires return."
        ),
        "bulk": (
            "Bulk operations: Must be processed by Account Management team. "
            "Not possible via support portal. Use escalate tool."
        ),
        "quota": (
            "API quota: Emergency increases require engineering approval. "
            "Escalate as P1 for enterprise accounts."
        ),
        "abuse": (
            "Refund abuse: More than 3 refunds in 90 days triggers abuse flag. "
            "Decline and cite policy. Do not process further refunds."
        ),
    },
}


def get_task_by_id(task_id: str) -> dict:
    """Fetch a task by its unique ID. Raises ValueError if not found."""
    for t in TASKS:
        if t["id"] == task_id:
            return t
    raise ValueError(f"Task {task_id!r} not found")


def get_tasks_by_difficulty(difficulty: str) -> list:
    """Return all tasks matching a given difficulty level."""
    return [t for t in TASKS if t["difficulty"] == difficulty]


def get_tool_response(tool: str, query: str) -> dict:
    """
    Look up a deterministic tool response.
    Tries exact match first, then substring match.
    Returns {"found": bool, "data": ...}
    """
    responses = TOOL_RESPONSES.get(tool, {})
    # Exact match
    if query in responses:
        return {"found": True, "data": responses[query]}
    # Substring match (e.g. "refund policy" matches key "refund")
    for key, value in responses.items():
        if key.lower() in query.lower():
            return {"found": True, "data": value}
    return {"found": False, "data": f"No results for '{query}'"}