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

HF_SPACE_URL = "https://shraddhashaha-omni-support-env.hf.space"

BENCHMARK         = "omni_support_env"
MAX_STEPS         = 12
TEMPERATURE       = 0.3
MAX_TOKENS        = 400
SUCCESS_THRESHOLD = 0.5

TASK_IDS = ["easy_refund_001", "med_chargeback_001", "hard_fraud_001"]

SYSTEM_PROMPT = """You are a customer support agent. You have access to tools.

Respond ONLY with valid JSON:
{"action_type": "<type>", "action_value": "<value>"}
"""


# ── Logging ──────────────────────────────────────────────────────────────────

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


# ── Safe HTTP client ─────────────────────────────────────────────────────────

class HttpEnvClient:
    def __init__(self, base_url: str):
        import httpx
        self._url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30.0)

    async def reset(self, task_id: Optional[str] = None):
        try:
            payload = {"task_id": task_id} if task_id else {}
            r = await self._http.post(f"{self._url}/reset", json=payload)
            r.raise_for_status()
            return _wrap(r.json())
        except Exception as e:
            print(f"[DEBUG] reset error: {e}", flush=True)
            return _safe_result()

    async def step(self, action):
        try:
            payload = {
                "action": {
                    "action_type": action.action_type.value,
                    "action_value": action.action_value,
                }
            }
            r = await self._http.post(f"{self._url}/step", json=payload)
            r.raise_for_status()
            return _wrap(r.json())
        except asyncio.CancelledError:
            print("[DEBUG] step cancelled", flush=True)
            return _safe_result(done=True)
        except Exception as e:
            print(f"[DEBUG] step error: {e}", flush=True)
            return _safe_result(done=True)

    async def close(self):
        try:
            await self._http.aclose()
        except Exception as e:
            print(f"[DEBUG] close error: {e}", flush=True)


class _Obs:
    def __init__(self, d: dict):
        self.__dict__.update(d)

class _Result:
    def __init__(self, data: dict):
        self.observation = _Obs(data.get("observation", {}))
        self.reward = data.get("reward", 0.0)
        self.done = data.get("done", False)

def _wrap(data: dict) -> _Result:
    return _Result(data)

def _safe_result(done=False):
    return _Result({
        "observation": {},
        "reward": 0.0,
        "done": done
    })


# ── LLM ──────────────────────────────────────────────────────────────────────

def parse_action(text: str):
    try:
        data = json.loads(text.strip())
        return data.get("action_type", "resolve"), str(data.get("action_value", "done"))
    except Exception:
        return "resolve", "error"


def get_action(client: OpenAI, prompt: str):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return parse_action(resp.choices[0].message.content or "")
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return "resolve", "fallback"


def format_obs(obs) -> str:
    return f"{getattr(obs,'ticket_text','')} | step info"


# ── Runner ───────────────────────────────────────────────────────────────────

async def run_task(env, client: OpenAI, task_id: str) -> float:
    from models import SupportAction, ActionType

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

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
            except:
                atype = ActionType.RESOLVE

            result = await env.step(
                SupportAction(action_type=atype, action_value=avalue)
            )

            reward = result.reward or 0.0
            done = result.done

            rewards.append(reward)
            steps_taken = step

            log_step(step, action_str, reward, done, None)

            if done:
                break

        score = max(0.0, min(1.0, sum(rewards)))
        success = score >= SUCCESS_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] run_task error: {e}", flush=True)

    finally:
        log_end(success, steps_taken, score, rewards)

    return score


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    env = HttpEnvClient(HF_SPACE_URL)

    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN or "dummy"
    )

    scores = []

    try:
        for task_id in TASK_IDS:
            score = await run_task(env, client, task_id)
            scores.append(score)
            print("", flush=True)
    finally:
        await env.close()

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"[SUMMARY] tasks={len(TASK_IDS)} avg_score={avg:.4f}", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[DEBUG] interrupted", flush=True)