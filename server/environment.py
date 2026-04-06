# server/environment.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from typing import Optional
from openenv.core.env_server import Environment
from models import SupportAction, SupportObservation, SupportState


PLACEHOLDER_TASK = {
    "id": "placeholder_001",
    "difficulty": "easy",
    "ticket": "I was charged twice for order #78234. I want a refund.",
    "user_id": "USR_4821",
    "account_tier": "premium",
    "account_age_days": 420,
    "ground_truth": {
        "resolution_type": "refund",
        "required_tools": ["lookup_order", "process_refund"],
        "correct_resolution_keywords": ["refund", "duplicate"],
        "should_escalate": False,
        "should_flag_security": False,
        "max_steps_expected": 6,
    },
}


class OmniSupportEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS = True
    MAX_STEPS = 15

    def __init__(self):
        self._task = PLACEHOLDER_TASK.copy()
        self._conversation = [{"role": "user", "content": PLACEHOLDER_TASK["ticket"]}]
        self._tool_results = []
        self._tools_used = []
        self._violations = []
        self._resolved = False
        self._resolution_type = ""
        self._did_escalate = False
        self._did_flag_security = False
        self._cumulative_reward = 0.0
        self._state = SupportState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            task_id=PLACEHOLDER_TASK["id"],
            task_difficulty=PLACEHOLDER_TASK["difficulty"],
            true_resolution=PLACEHOLDER_TASK["ground_truth"]["resolution_type"],
            required_tools=PLACEHOLDER_TASK["ground_truth"]["required_tools"],
            max_steps=self.MAX_STEPS,
        )

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        **kwargs,
    ) -> SupportObservation:
        self._task = PLACEHOLDER_TASK.copy()
        self._conversation = [{"role": "user", "content": self._task["ticket"]}]
        self._tool_results = []
        self._tools_used = []
        self._violations = []
        self._resolved = False
        self._resolution_type = ""
        self._did_escalate = False
        self._did_flag_security = False
        self._cumulative_reward = 0.0
        self._state = SupportState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=self._task["id"],
            task_difficulty=self._task["difficulty"],
            true_resolution=self._task["ground_truth"]["resolution_type"],
            required_tools=self._task["ground_truth"]["required_tools"],
            max_steps=self.MAX_STEPS,
        )
        return self._build_obs(reward=None, done=False,
                               feedback="New ticket received. Investigate and resolve.")

    def step(self, action: SupportAction, **kwargs) -> SupportObservation:
        self._state.step_count += 1
        return self._build_obs(
            reward=0.0,
            done=False,
            feedback=f"[STUB] Received action: {action.action_type}",
        )

    @property
    def state(self) -> SupportState:
        return self._state

    def _build_obs(self, reward, done, feedback) -> SupportObservation:
        return SupportObservation(
            done=done,
            reward=reward,
            ticket_id=self._state.task_id,
            ticket_text=self._task["ticket"],
            user_id=self._task["user_id"],
            account_tier=self._task["account_tier"],
            account_age_days=self._task["account_age_days"],
            conversation_history=list(self._conversation),
            tool_results=list(self._tool_results),
            policy_violations=list(self._violations),
            resolved=self._resolved,
            step_number=self._state.step_count,
            steps_remaining=self.MAX_STEPS - self._state.step_count,
            last_feedback=feedback,
            cumulative_reward=self._cumulative_reward,
        )