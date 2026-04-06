# test_phase3.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from reward import (
    resolution_score,
    tool_use_score,
    policy_score,
    efficiency_score,
    compute_step_reward,
    compute_episode_reward,
)
from tasks import get_task_by_id


def test_resolution_score():
    # Perfect resolution — all conditions met
    s = resolution_score(
        resolved=True,
        resolution_type_used="refund",
        ground_truth_resolution="refund",
        kw_found=["refund", "duplicate", "charged twice"],
        required_escalation=False,
        did_escalate=False,
        required_security_flag=False,
        did_flag_security=False,
    )
    assert 0.0 < s <= 1.0
    print(f"  ✓ resolution (perfect):          {s}")

    # Not resolved at all — must be 0
    s = resolution_score(
        resolved=False,
        resolution_type_used="",
        ground_truth_resolution="refund",
        kw_found=[],
        required_escalation=False,
        did_escalate=False,
        required_security_flag=False,
        did_flag_security=False,
    )
    assert s == 0.0
    print(f"  ✓ resolution (not resolved):     {s}")

    # Missed required security flag — heavy penalty
    s = resolution_score(
        resolved=True,
        resolution_type_used="refund",
        ground_truth_resolution="flag_fraud",
        kw_found=[],
        required_escalation=True,
        did_escalate=True,
        required_security_flag=True,
        did_flag_security=False,   # MISSED
    )
    assert s < 0.4
    print(f"  ✓ resolution (missed sec flag):  {s}  <- low, correct")


def test_tool_use_score():
    # Used exactly the right tools
    s = tool_use_score(
        ["lookup_order", "process_refund"],
        ["lookup_order", "process_refund"],
    )
    assert s == 1.0
    print(f"  ✓ tool_use (perfect):   {s}")

    # Only used half the required tools
    s = tool_use_score(
        ["lookup_order"],
        ["lookup_order", "process_refund"],
    )
    assert 0.0 < s < 1.0
    print(f"  ✓ tool_use (partial):   {s}")

    # Used nothing
    s = tool_use_score([], ["lookup_order", "process_refund"])
    assert s == 0.0
    print(f"  ✓ tool_use (nothing):   {s}")

    # No tools required — full score by default
    s = tool_use_score(["search_kb"], [])
    assert s == 1.0
    print(f"  ✓ tool_use (none req):  {s}")


def test_policy_score():
    assert policy_score([])                                  == 1.00
    assert policy_score(["REFUND_WITHOUT_ACCOUNT_CHECK"])    == 0.75
    assert policy_score(["V1", "V2"])                        == 0.50
    assert policy_score(["V1", "V2", "V3", "V4", "V5"])     == 0.00
    print("  ✓ policy: 0 violations=1.0 | 1=0.75 | 2=0.50 | 5+=0.0")


def test_efficiency_score():
    assert efficiency_score(4, 6)       == 1.0   # under budget
    assert efficiency_score(6, 6)       == 1.0   # exactly on budget
    s = efficiency_score(10, 6, 15)
    assert 0.0 < s < 1.0                         # over but within max
    assert efficiency_score(15, 6, 15)  == 0.0   # hit the wall
    print(f"  ✓ efficiency: under=1.0 | on=1.0 | over={s:.2f} | max=0.0")


def test_step_reward_positive():
    task = get_task_by_id("easy_refund_001")

    # First time using a required tool — positive signal
    r = compute_step_reward("lookup_order", "78234", task, [], [])
    assert r > 0
    print(f"  ✓ step reward (first req tool):  +{r}")

    # Same tool again — no bonus
    r2 = compute_step_reward("lookup_order", "78234", task, ["lookup_order"], [])
    assert r2 == 0.0
    print(f"  ✓ step reward (repeat req tool):  {r2}")

    # Meaningful message — small positive
    r3 = compute_step_reward("send_response", "Your refund has been processed.", task, [], [])
    assert r3 > 0
    print(f"  ✓ step reward (send response):   +{r3}")


def test_step_reward_traps():
    task = get_task_by_id("hard_fraud_001")

    # Falling into the refund trap — penalty
    r = compute_step_reward("process_refund", "78234,49.99,fraud", task, [], [])
    assert r < 0
    print(f"  ✓ step reward (refund trap):     {r}  <- negative, correct")

    # Correctly flagging security — positive
    r2 = compute_step_reward("flag_security", "USR_9901,fraud", task, [], [])
    assert r2 > 0
    print(f"  ✓ step reward (security flag):   +{r2}")

    # Correctly escalating
    r3 = compute_step_reward("escalate", "suspected fraud", task, [], [])
    assert r3 > 0
    print(f"  ✓ step reward (escalate):        +{r3}")


def test_episode_reward_good_agent():
    task = get_task_by_id("easy_refund_001")
    history = [
        {"role": "user",      "content": "I was charged twice"},
        {"role": "assistant", "content": "I see a duplicate charge, processing refund"},
    ]
    score = compute_episode_reward(
        resolved=True,
        resolution_type_used="refund",
        task=task,
        tools_used=["lookup_order", "process_refund"],
        violations=[],
        steps_taken=4,
        did_escalate=False,
        did_flag_security=False,
        conversation_history=history,
    )
    assert 0.0 <= score <= 1.0
    assert score > 0.4
    print(f"  ✓ episode reward (good easy agent):  {score}")


def test_episode_reward_fraud_trap():
    task = get_task_by_id("hard_fraud_001")

    # Bad agent: immediately refunds, never flags security
    score = compute_episode_reward(
        resolved=True,
        resolution_type_used="refund",
        task=task,
        tools_used=["process_refund"],
        violations=["REFUND_ON_SUSPICIOUS_NEW_ACCOUNT"],
        steps_taken=2,
        did_escalate=False,
        did_flag_security=False,
        conversation_history=[],
    )
    assert score < 0.20
    print(f"  ✓ episode reward (fell for fraud trap): {score}  <- very low, correct")


def test_scores_in_range():
    # Every output must be in [0.0, 1.0]
    for task in [
        get_task_by_id("easy_refund_001"),
        get_task_by_id("med_chargeback_001"),
        get_task_by_id("hard_fraud_001"),
    ]:
        score = compute_episode_reward(
            resolved=True,
            resolution_type_used="resolve",
            task=task,
            tools_used=["search_kb"],
            violations=[],
            steps_taken=8,
            did_escalate=False,
            did_flag_security=False,
            conversation_history=[],
        )
        assert 0.0 <= score <= 1.0, f"Score out of range for {task['id']}: {score}"
    print("  ✓ all episode scores stay in [0.0, 1.0]")


if __name__ == "__main__":
    print("\n=== PHASE 3 TESTS ===\n")
    test_resolution_score()
    test_tool_use_score()
    test_policy_score()
    test_efficiency_score()
    test_step_reward_positive()
    test_step_reward_traps()
    test_episode_reward_good_agent()
    test_episode_reward_fraud_trap()
    test_scores_in_range()
    print("\n✅ ALL PHASE 3 TESTS PASSED\n")