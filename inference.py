# inference.py
import asyncio
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from typing import List, Optional
from openai import OpenAI

# ── Environment variables ────────────────────────────────────────────────────
API_BASE_URL     = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME       = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN         = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# HF Space URL — used when no local Docker image is available
HF_SPACE_URL = "https://shraddhashaha-omni-support-env.hf.space"

BENCHMARK         = "omni_support_env"
MAX_STEPS         = 12
TEMPERATURE       = 0.3
MAX_TOKENS        = 400
SUCCESS_THRESHOLD = 0.5

TASK_IDS = ["easy_refund_001", "med_chargeback_001", "hard_fraud_001"]

SYSTEM_PROMPT = """You are a customer support agent. You have access to tools.

Respond ONLY with valid JSON — no explanation outside the JSON:
{"action_type": "<type>", "action_value": "<value>"}

ACTION TYPES:
- search_kb: <query>
- lookup_order: <order_id>
- check_account: <user_id>
- process_refund: <order_id,amount,reason>
- flag_security: <user_id,reason>
- ask_user: <question>
- send_response: <message>
- escalate: <reason>
- resolve: <summary>
- close_no_action: <reason>

RULES:
1. Always check_account before processing any refund
2. If fraud suspected: flag_security BEFORE any refund
3. If chargeback mentioned: escalate first, do not refund immediately
4. Gather information before resolving"""


# ── Mandatory stdout format ──────────────────────────────────────────────────

def log_start(task: str, model: str) -> None:
    print(f"[START] task={task} env={BENCHMARK} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ── HTTP client that talks to live HF Space (no Docker needed) ───────────────

class HttpEnvClient:
    """
    Thin HTTP client that connects to the live HF Space REST API.
    Used by the validator — no Docker image required on their machine.
    """
    def __init__(self, base_url: str):
        import httpx
        self._url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=60.0)

    async def reset(self, task_id: Optional[str] = None):
        payload = {}
        if task_id:
            payload["task_id"] = task_id
        r = await self._http.post(f"{self._url}/reset", json=payload)
        r.raise_for_status()
        return _wrap(r.json())

    async def step(self, action):
        payload = {
            "action": {
                "action_type": action.action_type.value,
                "action_value": action.action_value,
            }
        }
        r = await self._http.post(f"{self._url}/step", json=payload)
        r.raise_for_status()
        return _wrap(r.json())

    async def close(self):
        await self._http.aclose()


class _Obs:
    def __init__(self, d: dict):
        self.__dict__.update(d)

class _Result:
    def __init__(self, data: dict):
        obs_data = data.get("observation", {})
        self.observation = _Obs(obs_data)
        self.reward = data.get("reward") or 0.0
        self.done = data.get("done", False)

def _wrap(data: dict) -> _Result:
    return _Result(data)


# ── LLM agent ────────────────────────────────────────────────────────────────

def parse_action(text: str):
    try:
        clean = text.strip()
        if "```" in clean:
            parts = clean.split("```")
            clean = parts[1] if len(parts) > 1 else clean
            if clean.startswith("json"):
                clean = clean[4:]
        data = json.loads(clean.strip())
        return data.get("action_type", "resolve"), str(data.get("action_value", "done"))
    except Exception:
        return "resolve", "could not parse response"


def get_action(client: OpenAI, obs_text: str):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": obs_text},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return parse_action(resp.choices[0].message.content or "")
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return "resolve", "error"


def format_obs(obs) -> str:
    last_tool = ""
    if getattr(obs, "tool_results", None):
        last_tool = f"\nLast tool result: {json.dumps(obs.tool_results[-1])}"
    violations = ""
    if getattr(obs, "policy_violations", None):
        violations = f"\nVIOLATIONS: {obs.policy_violations}"
    return (
        f"TICKET #{getattr(obs,'ticket_id','')} | "
        f"User: {getattr(obs,'user_id','')} | "
        f"Tier: {getattr(obs,'account_tier','')} | "
        f"Account age: {getattr(obs,'account_age_days',0)} days\n\n"
        f"ISSUE: {getattr(obs,'ticket_text','')}\n\n"
        f"Step {getattr(obs,'step_number',0)}/{MAX_STEPS} | "
        f"Remaining: {getattr(obs,'steps_remaining',MAX_STEPS)} | "
        f"Reward so far: {getattr(obs,'cumulative_reward',0.0):.2f}\n"
        f"Feedback: {getattr(obs,'last_feedback','')}"
        f"{last_tool}{violations}\n\n"
        f"What is your next action? JSON only."
    )


# ── Episode runner ────────────────────────────────────────────────────────────

async def run_task(env, client: OpenAI, task_id: str) -> float:
    from models import SupportAction, ActionType

    rewards: List[float] = []
    steps_taken = 0
    score       = 0.0
    success     = False

    log_start(task=task_id, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=task_id)

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            atype_str, avalue = get_action(client, format_obs(result.observation))
            action_str = f"{atype_str}:{avalue[:40]}"

            try:
                atype = ActionType(atype_str)
            except ValueError:
                atype = ActionType.RESOLVE

            result = await env.step(
                SupportAction(action_type=atype, action_value=avalue)
            )

            reward = result.reward or 0.0
            done   = result.done
            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=action_str, reward=reward, done=done, error=None)

            if done:
                break

        score   = max(0.0, min(1.0, sum(rewards)))
        success = score >= SUCCESS_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Task error: {e}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    # Connect to live HF Space — works on any machine, no Docker needed
    env = HttpEnvClient(HF_SPACE_URL)

    # OpenAI client — uses HF_TOKEN if set, falls back gracefully for LLM calls
    api_key = HF_TOKEN or "dummy"
    client  = OpenAI(base_url=API_BASE_URL, api_key=api_key)

    all_scores: List[float] = []

    print(f"[INFO] Model:     {MODEL_NAME}", flush=True)
    print(f"[INFO] Tasks:     {TASK_IDS}", flush=True)
    print(f"[INFO] Space URL: {HF_SPACE_URL}", flush=True)
    print("", flush=True)

    try:
        for task_id in TASK_IDS:
            score = await run_task(env, client, task_id)
            all_scores.append(score)
            print("", flush=True)
    finally:
        await env.close()

    avg = sum(all_scores) / len(all_scores) if all_scores else 0.0
    print(f"[SUMMARY] tasks={len(TASK_IDS)} avg_score={avg:.4f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())