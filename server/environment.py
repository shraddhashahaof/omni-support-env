# server/environment.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import uuid
from typing import List, Dict, Any, Optional

from openenv.core.env_server import Environment
from models import SupportAction, SupportObservation, SupportState, ActionType
from tasks import TASKS, get_task_by_id, get_tasks_by_difficulty
from tools import execute_tool
from reward import compute_step_reward
from graders import grade_episode


class OmniSupportEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS = True
    MAX_STEPS = 15

    def __init__(self):
        self._task: Dict[str, Any]        = self._placeholder_task()
        self._conversation: List[Dict]    = []
        self._tool_results: List[Dict]    = []
        self._tools_used: List[str]       = []
        self._violations: List[str]       = []
        self._resolved                    = False
        self._resolution_type             = ""
        self._did_escalate                = False
        self._did_flag_security           = False
        self._cumulative_reward           = 0.0
        self._state = self._make_state(str(uuid.uuid4()))

    # ── reset ────────────────────────────────────────────────
    def reset(self, seed=None, episode_id=None, task_id=None, difficulty=None, **kwargs) -> SupportObservation:
        if task_id:
            self._task = get_task_by_id(task_id)
        elif difficulty:
            self._task = random.choice(get_tasks_by_difficulty(difficulty))
        else:
            self._task = random.choice(TASKS)

        self._conversation      = []
        self._tool_results      = []
        self._tools_used        = []
        self._violations        = []
        self._resolved          = False
        self._resolution_type   = ""
        self._did_escalate      = False
        self._did_flag_security = False
        self._cumulative_reward = 0.0
        self._state             = self._make_state(episode_id or str(uuid.uuid4()))

        self._conversation.append({"role": "system",
            "content": "You are a customer support agent. Resolve the ticket. Follow all policies."})
        self._conversation.append({"role": "user", "content": self._task["ticket"]})

        return self._build_obs(reward=None, done=False, feedback="New ticket received. Investigate and resolve.")

    # ── step ─────────────────────────────────────────────────
    def step(self, action: SupportAction, timeout_s=None, **kwargs) -> SupportObservation:
        self._state.step_count += 1
        atype  = action.action_type.value
        avalue = action.action_value
        feedback = ""

        if atype in ("search_kb", "lookup_order", "check_account",
                     "process_refund", "flag_security",
                     "ask_user", "send_response", "escalate"):
            result = execute_tool(atype, avalue)
            self._tool_results.append(result)
            if atype not in self._tools_used:
                self._tools_used.append(atype)
                self._state.tools_used = list(self._tools_used)
            feedback = f"Tool '{atype}': {result.get('message', result.get('result', 'done'))}"
            if atype == "escalate":      self._did_escalate      = True
            if atype == "flag_security": self._did_flag_security = True
            self._conversation.append({"role": "assistant", "content": f"[TOOL:{atype}] {avalue}"})
            self._conversation.append({"role": "tool",      "content": str(result)})

        elif atype in ("resolve", "close_no_action"):
            self._resolved        = True
            self._resolution_type = atype
            feedback = f"Resolution: {atype}"
            self._conversation.append({"role": "assistant", "content": f"[RESOLVE:{atype}] {avalue}"})

        violations = self._check_policy(atype, avalue)
        self._violations.extend(violations)
        self._state.policy_violations = list(self._violations)
        if violations:
            feedback += f" | POLICY VIOLATION: {'; '.join(violations)}"

        done = self._is_done()

        if done:
            reward = grade_episode(
                episode_state={
                    "resolved":             self._resolved,
                    "resolution_type_used": self._resolution_type,
                    "tools_used":           list(self._tools_used),
                    "policy_violations":    list(self._violations),
                    "steps_taken":          self._state.step_count,
                    "did_escalate":         self._did_escalate,
                    "did_flag_security":    self._did_flag_security,
                    "conversation_history": list(self._conversation),
                },
                task=self._task,
            )
        else:
            reward = compute_step_reward(
                action_type=atype,
                action_value=avalue,
                task=self._task,
                tools_used_so_far=list(self._tools_used),
                violations_so_far=list(self._violations),
            )

        self._cumulative_reward      += reward
        self._state.total_reward      = self._cumulative_reward
        return self._build_obs(reward=reward, done=done, feedback=feedback)

    @property
    def state(self) -> SupportState:
        return self._state

    # ── helpers ──────────────────────────────────────────────
    def _build_obs(self, reward, done, feedback) -> SupportObservation:
        return SupportObservation(
            done=done, reward=reward,
            ticket_id=self._state.task_id,
            ticket_text=self._task.get("ticket", ""),
            user_id=self._task.get("user_id", ""),
            account_tier=self._task.get("account_tier", "free"),
            account_age_days=self._task.get("account_age_days", 0),
            conversation_history=list(self._conversation),
            tool_results=list(self._tool_results),
            policy_violations=list(self._violations),
            resolved=self._resolved,
            step_number=self._state.step_count,
            steps_remaining=self.MAX_STEPS - self._state.step_count,
            last_feedback=feedback,
            cumulative_reward=self._cumulative_reward,
        )

    def _is_done(self) -> bool:
        return self._resolved or self._state.step_count >= self.MAX_STEPS

    def _check_policy(self, atype, avalue) -> List[str]:
        violations = []
        gt     = self._task.get("ground_truth", {})
        ticket = self._task.get("ticket", "").lower()

        if atype == "process_refund" and "check_account" not in self._tools_used:
            violations.append("REFUND_WITHOUT_ACCOUNT_CHECK")

        if (atype == "process_refund"
                and self._task.get("account_age_days", 999) < 30
                and gt.get("should_flag_security")):
            violations.append("REFUND_ON_SUSPICIOUS_NEW_ACCOUNT")

        if ("chargeback" in ticket and atype == "process_refund" and not self._did_escalate):
            violations.append("REFUND_DURING_CHARGEBACK")

        if "gdpr" in ticket and atype == "close_no_action":
            violations.append("GDPR_REQUEST_CLOSED_WITHOUT_ROUTING")

        return violations

    def _make_state(self, episode_id: str) -> SupportState:
        return SupportState(
            episode_id=episode_id, step_count=0,
            task_id=self._task["id"],
            task_difficulty=self._task["difficulty"],
            true_resolution=self._task["ground_truth"]["resolution_type"],
            required_tools=self._task["ground_truth"]["required_tools"],
            max_steps=self.MAX_STEPS,
        )

    @staticmethod
    def _placeholder_task() -> Dict[str, Any]:
        return {
            "id": "placeholder_001", "difficulty": "easy",
            "ticket": "I was charged twice for order #78234. I want a refund.",
            "user_id": "USR_4821", "account_tier": "premium", "account_age_days": 420,
            "ground_truth": {
                "resolution_type": "refund",
                "required_tools": ["lookup_order", "process_refund"],
                "correct_resolution_keywords": ["refund", "duplicate"],
                "should_escalate": False, "should_flag_security": False, "max_steps_expected": 6,
            },
        }