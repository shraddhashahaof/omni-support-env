# test_phase4.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from environment import OmniSupportEnvironment
from models import SupportAction, ActionType
from graders import grade_episode
from tasks import get_task_by_id


def run_scripted_episode(task_id: str, actions: list) -> tuple:
    """
    Run a scripted episode with a fixed sequence of actions.
    Returns (final_obs, list_of_rewards).
    """
    env = OmniSupportEnvironment()
    env.reset(task_id=task_id)
    rewards = []
    obs     = None
    for atype, avalue in actions:
        obs = env.step(SupportAction(
            action_type=ActionType(atype),
            action_value=avalue,
        ))
        rewards.append(obs.reward or 0.0)
        if obs.done:
            break
    return obs, rewards


def test_easy_good_agent():
    print("\n  [EASY] good agent — checks account, looks up order, refunds:")
    obs, rewards = run_scripted_episode("easy_refund_001", [
        ("check_account",  "USR_4821"),
        ("lookup_order",   "78234"),
        ("process_refund", "78234, 49.99, duplicate charge"),
        ("send_response",  "I have processed a full refund for the duplicate charge."),
        ("resolve",        "Duplicate charge refunded. Ticket closed."),
    ])
    assert obs.done is True
    assert obs.reward is not None
    assert obs.reward > 0.0
    print(f"  ✓ done=True | step_rewards={[round(r,2) for r in rewards]}")
    print(f"  ✓ final_score={obs.reward} | cumulative={obs.cumulative_reward:.2f}")
    return obs.reward


def test_easy_bad_agent():
    print("\n  [EASY] bad agent — refunds without checking account first:")
    obs, rewards = run_scripted_episode("easy_refund_001", [
        ("process_refund", "78234, 49.99, just do it"),
        ("resolve",        "done"),
    ])
    assert obs.done is True
    assert "REFUND_WITHOUT_ACCOUNT_CHECK" in obs.policy_violations
    print(f"  ✓ policy_violations={obs.policy_violations}")
    print(f"  ✓ final_score={obs.reward}  <- penalised, correct")
    return obs.reward


def test_medium_chargeback():
    print("\n  [MEDIUM] agent handles chargeback correctly:")
    obs, rewards = run_scripted_episode("med_chargeback_001", [
        ("check_account",  "USR_2209"),
        ("lookup_order",   "66112"),
        ("search_kb",      "chargeback policy"),
        ("escalate",       "Customer filed chargeback, billing specialist needed"),
        ("send_response",  "I have escalated your case. Specialist will contact you within 24h."),
        ("resolve",        "Escalated to billing specialist due to chargeback."),
    ])
    assert obs.done is True
    assert obs.reward > 0.0
    print(f"  ✓ final_score={obs.reward}")
    return obs.reward


def test_hard_fraud_good_agent():
    print("\n  [HARD] good agent — flags security, escalates, does NOT refund:")
    obs, rewards = run_scripted_episode("hard_fraud_001", [
        ("check_account",  "USR_9901"),
        ("search_kb",      "fraud policy"),
        ("flag_security",  "USR_9901, 3 unauthorized transactions totalling $847"),
        ("escalate",       "Suspected fraud on new account with risk score 0.87"),
        ("send_response",  "We have flagged this for security review. Please do not share OTP."),
        ("resolve",        "Fraud flagged and escalated. Account under security review."),
    ])
    assert obs.done is True
    print(f"  ✓ final_score={obs.reward}")
    return obs.reward


def test_hard_fraud_bad_agent():
    print("\n  [HARD] bad agent — immediately refunds fraud account (falls for trap):")
    obs, rewards = run_scripted_episode("hard_fraud_001", [
        ("process_refund", "unknown, 847, unauthorized"),
        ("resolve",        "Refunded."),
    ])
    assert obs.done is True
    assert obs.reward < 0.20
    print(f"  ✓ final_score={obs.reward}  <- very low, agent fell for trap")
    return obs.reward


def test_step_limit():
    print("\n  [LIMIT] episode terminates at step limit:")
    env = OmniSupportEnvironment()
    env.reset(task_id="easy_refund_001")
    obs = None
    for _ in range(20):
        obs = env.step(SupportAction(
            action_type=ActionType.SEARCH_KB,
            action_value="test",
        ))
        if obs.done:
            break
    assert obs.done is True
    assert obs.step_number <= 15
    print(f"  ✓ done=True at step {obs.step_number}")


def test_reset_gives_clean_state():
    print("\n  [RESET] reset() gives clean state every time:")
    env = OmniSupportEnvironment()

    obs1 = env.reset(task_id="easy_refund_001")
    env.step(SupportAction(action_type=ActionType.SEARCH_KB, action_value="test"))
    env.step(SupportAction(action_type=ActionType.SEARCH_KB, action_value="test"))

    # Reset should wipe all episode state
    obs2 = env.reset(task_id="easy_refund_001")
    assert obs2.step_number      == 0
    assert obs2.cumulative_reward == 0.0
    assert obs2.policy_violations == []
    assert obs2.resolved          is False
    print(f"  ✓ step_number=0, cumulative=0.0, violations=[], resolved=False")


def test_scores_differ_correctly():
    good_easy  = test_easy_good_agent()
    bad_easy   = test_easy_bad_agent()
    good_hard  = test_hard_fraud_good_agent()
    bad_hard   = test_hard_fraud_bad_agent()

    print(f"\n  Score comparison:")
    print(f"    Easy  good agent: {good_easy:.4f}")
    print(f"    Easy  bad agent:  {bad_easy:.4f}")
    print(f"    Hard  good agent: {good_hard:.4f}")
    print(f"    Hard  bad agent:  {bad_hard:.4f}")

    assert good_easy > bad_easy,  "Good easy agent should outscore bad easy agent"
    assert good_hard > bad_hard,  "Good hard agent should outscore bad hard agent"
    print("  ✓ Good agents consistently outscore bad agents")


if __name__ == "__main__":
    print("\n=== PHASE 4 TESTS ===")
    test_easy_good_agent()
    test_easy_bad_agent()
    test_medium_chargeback()
    test_hard_fraud_good_agent()
    test_hard_fraud_bad_agent()
    test_step_limit()
    test_reset_gives_clean_state()
    test_scores_differ_correctly()
    print("\n✅ ALL PHASE 4 TESTS PASSED\n")