# test_phase2.py
"""
Phase 2 tests — tasks and tools.
Run from project root: python test_phase2.py
All tests are deterministic — same output every run.
"""
import sys
sys.path.insert(0, "server")

from tasks import TASKS, get_task_by_id, get_tasks_by_difficulty
from tools import (
    execute_tool, search_knowledge_base,
    lookup_order, check_account, process_refund,
    flag_security, escalate_ticket,
)


def test_tasks_load():
    """Verify all 15 tasks loaded with correct distribution."""
    assert len(TASKS) == 15, f"Expected 15 tasks, got {len(TASKS)}"
    easy   = get_tasks_by_difficulty("easy")
    medium = get_tasks_by_difficulty("medium")
    hard   = get_tasks_by_difficulty("hard")
    assert len(easy)   == 5, f"Expected 5 easy, got {len(easy)}"
    assert len(medium) == 5, f"Expected 5 medium, got {len(medium)}"
    assert len(hard)   == 5, f"Expected 5 hard, got {len(hard)}"
    print(f"  ✓ 15 tasks loaded: {len(easy)} easy / {len(medium)} medium / {len(hard)} hard")


def test_task_structure():
    """Every task must have required fields and ground truth keys."""
    required_fields = ["id", "difficulty", "ticket", "user_id",
                       "account_tier", "account_age_days", "ground_truth"]
    required_gt = ["required_tools", "should_escalate",
                   "should_flag_security", "max_steps_expected"]
    for t in TASKS:
        for f in required_fields:
            assert f in t, f"Task {t.get('id')} missing field: {f}"
        for g in required_gt:
            assert g in t["ground_truth"], \
                f"Task {t.get('id')} ground_truth missing: {g}"
    print("  ✓ All 15 tasks have correct structure")


def test_get_task_by_id():
    """Task lookup by ID works correctly."""
    t = get_task_by_id("easy_refund_001")
    assert t["difficulty"] == "easy"
    assert t["user_id"] == "USR_4821"

    t2 = get_task_by_id("hard_fraud_001")
    assert t2["ground_truth"]["should_flag_security"] is True
    assert "trap" in t2["ground_truth"]

    # Non-existent task raises ValueError
    try:
        get_task_by_id("does_not_exist")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  ✓ get_task_by_id works, invalid ID raises ValueError")


def test_search_kb():
    """KB search returns relevant policy text."""
    r = search_knowledge_base("refund policy")
    assert r["tool"] == "search_kb"
    assert r["found"] is True
    assert "30 days" in r["result"]
    print(f"  ✓ search_kb 'refund': found={r['found']}, snippet='{r['result'][:50]}...'")

    # Fraud policy
    r2 = search_knowledge_base("fraud detection")
    assert r2["found"] is True
    assert "flag_security" in r2["result"]
    print(f"  ✓ search_kb 'fraud': found={r2['found']}")


def test_lookup_order():
    """Order lookup returns correct data including duplicate charge flag."""
    r = lookup_order("#78234")
    assert r["found"] is True
    assert r["result"]["duplicate_charge"] is True
    assert r["result"]["amount"] == 49.99
    print(f"  ✓ lookup_order #78234: duplicate_charge={r['result']['duplicate_charge']}, amount={r['result']['amount']}")

    # In-transit order
    r2 = lookup_order("90221")
    assert r2["found"] is True
    assert r2["result"]["status"] == "in_transit"
    print(f"  ✓ lookup_order 90221: status={r2['result']['status']}, carrier={r2['result']['carrier']}")

    # Unknown order
    r3 = lookup_order("99999")
    assert r3["found"] is False
    print(f"  ✓ lookup_order unknown: found={r3['found']}")


def test_check_account():
    """Account check returns correct flags and risk scores."""
    # Normal account
    r = check_account("USR_4821")
    assert r["found"] is True
    assert r["result"]["flags"] == []
    print(f"  ✓ check_account USR_4821: clean account, flags={r['result']['flags']}")

    # High-risk fraud account
    r2 = check_account("USR_9901")
    assert r2["found"] is True
    assert "new_account" in r2["result"]["flags"]
    assert r2["result"]["risk_score"] > 0.8
    print(f"  ✓ check_account USR_9901: risk_score={r2['result']['risk_score']}, flags={r2['result']['flags']}")

    # Refund abuser
    r3 = check_account("USR_7733")
    assert "refund_abuse_flag" in r3["result"]["flags"]
    assert r3["result"]["refund_count_90_days"] >= 4
    print(f"  ✓ check_account USR_7733: abuse flag present, refunds={r3['result']['refund_count_90_days']}")


def test_process_refund():
    """Refund tool returns confirmation ID."""
    r = process_refund("78234", "49.99", "duplicate charge")
    assert r["status"] == "processed"
    assert r["amount"] == 49.99
    assert "REF-78234" in r["confirmation_id"]
    print(f"  ✓ process_refund: status={r['status']}, confirmation={r['confirmation_id']}")


def test_flag_security():
    """Security flag tool returns correct status."""
    r = flag_security("USR_9901", "3 unauthorized transactions")
    assert r["status"] == "flagged"
    assert "USR_9901" in r["message"]
    print(f"  ✓ flag_security: {r['message']}")


def test_escalate():
    """Escalation tool returns correct assignment."""
    r = escalate_ticket("chargeback dispute", "high")
    assert r["status"] == "escalated"
    assert r["priority"] == "high"
    print(f"  ✓ escalate: priority={r['priority']}, assigned_to={r['assigned_to']}")


def test_execute_tool_router():
    """Router correctly dispatches all action types."""
    # All tool types
    cases = [
        ("search_kb",      "chargeback policy",          "found"),
        ("lookup_order",   "78234",                      "tool"),
        ("check_account",  "USR_4821",                   "tool"),
        ("process_refund", "78234, 49.99, test",         "status"),
        ("flag_security",  "USR_9901, fraud",            "status"),
        ("escalate",       "billing dispute, normal",    "status"),
        ("ask_user",       "What is your order number?", "status"),
        ("send_response",  "Your refund is processed.",  "status"),
    ]
    for action_type, action_value, check_key in cases:
        r = execute_tool(action_type, action_value)
        assert check_key in r, f"Tool {action_type} missing key '{check_key}' in response"
        assert r.get("status") != "failed", f"Tool {action_type} returned failed status"
        print(f"  ✓ execute_tool '{action_type}': OK")

    # Unknown tool handled gracefully
    r = execute_tool("fly_to_moon", "whatever")
    assert r["status"] == "unknown_tool"
    print(f"  ✓ unknown tool 'fly_to_moon': handled gracefully")


if __name__ == "__main__":
    print("\n=== PHASE 2 TESTS ===\n")
    test_tasks_load()
    test_task_structure()
    test_get_task_by_id()
    test_search_kb()
    test_lookup_order()
    test_check_account()
    test_process_refund()
    test_flag_security()
    test_escalate()
    test_execute_tool_router()
    print("\n✅ ALL PHASE 2 TESTS PASSED\n")