"""
collect_training_data.py
Runs the OmniSupportEnv locally and saves rollouts as GRPO-ready JSONL.
Each record: {"prompt": [...messages], "completion": action_str, "reward": float}

Usage:
    python collect_training_data.py --episodes 200 --out data/rollouts.jsonl
"""
import sys, os, json, argparse, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from environment import OmniSupportEnvironment
from tasks import TASKS

TOOL_ACTIONS = [
    "search_kb", "lookup_order", "check_account",
    "process_refund", "flag_security", "escalate",
    "ask_user", "send_response",
]
RESOLVE_ACTIONS = ["resolve", "close_no_action"]

SYSTEM_PROMPT = (
    "You are a customer support agent. Given the ticket and conversation so far, "
    "choose the BEST next action.\n"
    "Output format (one line only):\n"
    "ACTION: <action_type> | VALUE: <action_value>\n\n"
    "Available action_types: search_kb, lookup_order, check_account, process_refund, "
    "flag_security, escalate, ask_user, send_response, resolve, close_no_action\n"
    "Examples:\n"
    "  ACTION: check_account | VALUE: USR_4821\n"
    "  ACTION: lookup_order | VALUE: 78234\n"
    "  ACTION: resolve | VALUE: Refund processed for duplicate charge.\n"
)


def heuristic_agent(obs, task):
    """
    Simple rule-based agent that roughly follows correct policy.
    Provides non-zero reward training signal without needing an LLM.
    """
    gt = task["ground_truth"]
    required = gt.get("required_tools", [])
    tools_used = obs.tool_results
    used_types = {r["tool"] for r in tools_used}

    # Pick next required tool not yet used
    for tool in required:
        if tool not in used_types:
            # Pick sensible value
            if tool == "check_account":
                return tool, task.get("user_id", "USR_0000")
            elif tool == "lookup_order":
                ticket = task.get("ticket", "")
                import re
                m = re.search(r"#?(\d{4,})", ticket)
                return tool, m.group(1) if m else "78234"
            elif tool == "process_refund":
                ticket = task.get("ticket", "")
                import re
                m = re.search(r"#?(\d{4,})", ticket)
                oid = m.group(1) if m else "78234"
                return tool, f"{oid}, 29.99, duplicate charge"
            elif tool == "flag_security":
                return tool, f"{task.get('user_id','USR_0000')}, suspicious activity"
            elif tool == "escalate":
                return tool, f"requires specialist review, normal"
            elif tool == "search_kb":
                # Extract keyword from ticket
                ticket = task.get("ticket", "").lower()
                for kw in ["refund","password","cancel","chargeback","fraud","gdpr","billing","damaged","bulk","quota","abuse","enterprise"]:
                    if kw in ticket:
                        return tool, kw
                return tool, "refund"
            else:
                return tool, "general query"

    # All required tools used → resolve
    rt = gt.get("resolution_type", "resolve")
    kws = gt.get("correct_resolution_keywords", [])
    msg = f"{rt}. {' '.join(kws[:2])}" if kws else rt
    return "resolve", msg


def noisy_agent(obs, task, noise=0.25):
    """Add random wrong actions to create negative examples."""
    if random.random() < noise:
        bad = random.choice(["process_refund", "close_no_action", "escalate"])
        return bad, "random noise"
    return heuristic_agent(obs, task)


def collect(num_episodes=300, out_path="data/rollouts.jsonl", noise_ratio=0.3):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    env = OmniSupportEnvironment()
    records = []

    for ep in range(num_episodes):
        task = random.choice(TASKS)
        obs = env.reset(task_id=task["id"])
        use_noise = (ep % 3 == 0)  # 1/3 noisy episodes for negative examples

        step_prompts = []  # accumulate per-step

        for _ in range(env.MAX_STEPS):
            # Build prompt from current conversation
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages += obs.conversation_history
            if obs.tool_results:
                messages.append({
                    "role": "user",
                    "content": f"Tool results so far: {json.dumps(obs.tool_results[-3:])}\n"
                               f"Steps remaining: {obs.steps_remaining}\n"
                               "What is your next action?"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"Steps remaining: {obs.steps_remaining}\nWhat is your next action?"
                })

            # Choose action
            if use_noise:
                atype, avalue = noisy_agent(obs, task)
            else:
                atype, avalue = heuristic_agent(obs, task)

            completion = f"ACTION: {atype} | VALUE: {avalue}"

            # Step env
            from models import SupportAction, ActionType
            try:
                action = SupportAction(
                    action_type=ActionType(atype),
                    action_value=avalue
                )
            except Exception:
                break

            obs = env.step(action)

            step_prompts.append({
                "prompt": messages,
                "completion": completion,
                "reward": obs.reward if obs.reward is not None else 0.0,
                "task_id": task["id"],
                "difficulty": task["difficulty"],
                "step": obs.step_number,
            })

            if obs.done:
                # Assign final episode reward to all steps (credit assignment)
                final_r = obs.cumulative_reward
                for rec in step_prompts:
                    # Blend step reward with final outcome signal
                    rec["reward"] = round(0.4 * rec["reward"] + 0.6 * final_r, 4)
                records.extend(step_prompts)
                break

        if (ep + 1) % 50 == 0:
            print(f"  [{ep+1}/{num_episodes}] collected {len(records)} steps")

    with open(out_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    print(f"\n✅ Saved {len(records)} training records → {out_path}")
    # Print reward distribution
    rewards = [r["reward"] for r in records]
    print(f"   Reward: min={min(rewards):.3f}  mean={sum(rewards)/len(rewards):.3f}  max={max(rewards):.3f}")
    pos = sum(1 for r in rewards if r > 0.3)
    print(f"   Positive (>0.3): {pos}/{len(records)} = {100*pos//len(records)}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=300)
    parser.add_argument("--out", default="data/rollouts.jsonl")
    args = parser.parse_args()
    collect(args.episodes, args.out)