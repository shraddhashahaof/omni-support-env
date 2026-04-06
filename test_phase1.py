# test_phase1.py
"""Phase 1 smoke test — models instantiate, reset() works."""
import sys
sys.path.insert(0, "server")

from models import SupportAction, SupportObservation, SupportState, ActionType
from server.environment import OmniSupportEnvironment


def test_models_instantiate():
    action = SupportAction(action_type=ActionType.RESOLVE, action_value="done")
    assert action.action_type == ActionType.RESOLVE
    print("  ✓ SupportAction instantiates")

    state = SupportState(task_id="test", task_difficulty="easy")
    assert state.task_id == "test"
    print("  ✓ SupportState instantiates")


def test_reset():
    env = OmniSupportEnvironment()
    obs = env.reset()

    assert isinstance(obs, SupportObservation)
    assert obs.done is False
    assert obs.reward is None
    assert len(obs.ticket_text) > 0
    assert obs.step_number == 0
    assert obs.steps_remaining == 15
    print("  ✓ reset() returns valid SupportObservation")
    print(f"  ✓ Ticket: {obs.ticket_text[:60]}...")
    print(f"  ✓ User: {obs.user_id}, Tier: {obs.account_tier}")


def test_state_after_reset():
    env = OmniSupportEnvironment()
    env.reset()
    s = env.state
    assert s.step_count == 0
    assert s.episode_id is not None
    assert len(s.episode_id) > 0
    print(f"  ✓ State: episode_id={s.episode_id[:8]}..., steps={s.step_count}")


def test_stub_step():
    env = OmniSupportEnvironment()
    env.reset()
    action = SupportAction(action_type=ActionType.SEARCH_KB, action_value="refund policy")
    obs = env.step(action)
    assert obs.step_number == 1
    assert obs.steps_remaining == 14
    print(f"  ✓ step() stub works: step={obs.step_number}, feedback={obs.last_feedback}")


if __name__ == "__main__":
    print("\n=== PHASE 1 TESTS ===\n")
    test_models_instantiate()
    test_reset()
    test_state_after_reset()
    test_stub_step()
    print("\n✅ ALL PHASE 1 TESTS PASSED\n")