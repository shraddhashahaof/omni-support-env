# inference.py
import asyncio
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Environment variables — mandatory format from submission guidelines ──────
API_BASE_URL     = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME       = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN         = os.getenv("HF_TOKEN")         
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")   

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

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


# ── Mandatory stdout format — do not change field names or order ─────────────

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


# ── LLM agent ────────────────────────────────────────────────────────────────

def parse_action(text: str):
    try:
        clean = text.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
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
    if obs.tool_results:
        last_tool = f"\nLast tool result: {json.dumps(obs.tool_results[-1])}"
    violations = f"\nVIOLATIONS: {obs.policy_violations}" if obs.policy_violations else ""
    return (
        f"TICKET #{obs.ticket_id} | User: {obs.user_id} | "
        f"Tier: {obs.account_tier} | Account age: {obs.account_age_days} days\n\n"
        f"ISSUE: {obs.ticket_text}\n\n"
        f"Step {obs.step_number}/{MAX_STEPS} | Remaining: {obs.steps_remaining} | "
        f"Reward so far: {obs.cumulative_reward:.2f}\n"
        f"Feedback: {obs.last_feedback}"
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

            result = await env.step(SupportAction(action_type=atype, action_value=avalue))

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

async def main():
    from client import OmniSupportEnvClient as OmniSupportEnv

    # Initialize OpenAI client pointing at HuggingFace router
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    all_scores: List[float] = []

    print(f"[INFO] Model:  {MODEL_NAME}", flush=True)
    print(f"[INFO] Tasks:  {TASK_IDS}", flush=True)
    print("", flush=True)

    env = await OmniSupportEnv.from_docker_image(LOCAL_IMAGE_NAME)
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