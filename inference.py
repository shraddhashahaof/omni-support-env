# inference.py  — OmniSupportEnv  (local + remote modes)
import asyncio, json, os, sys, time
from dotenv import load_dotenv
load_dotenv()

from typing import List, Optional
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL", "https://shraddhashaha-omni-support-env.hf.space")

# Set USE_LOCAL=1 in .env to bypass the HF space and run fully locally
USE_LOCAL = os.getenv("USE_LOCAL", "0").strip() == "1"

BENCHMARK         = "omni_support_env"
MAX_STEPS         = 12
TEMPERATURE       = 0.2
MAX_TOKENS        = 512
SUCCESS_THRESHOLD = 0.5

TASK_IDS = [
    "easy_refund_001", "easy_password_001", "easy_cancel_001",
    "easy_delivery_001", "easy_update_001",
    "med_chargeback_001", "med_partial_refund_001", "med_tech_billing_001",
    "med_subscription_dispute_001", "med_api_quota_001",
    "hard_fraud_001", "hard_abuse_001", "hard_enterprise_breach_001",
    "hard_bulk_001", "hard_gdpr_001",
]
DIFFICULTY_MAP = {"easy": "EASY  ", "med": "MEDIUM", "hard": "HARD  "}

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a customer support agent. Resolve support tickets step-by-step.

AVAILABLE ACTIONS (use exactly one per turn):
- search_kb       : search policy docs (keywords: refund, cancel, fraud, chargeback, gdpr, password, damaged, bulk, quota, enterprise, abuse)
- lookup_order    : get order details — value = the order ID from the ticket (e.g. "78234")
- check_account   : get account info — value = the user_id shown in the prompt (e.g. "USR_4821")
- process_refund  : issue refund     — value = "order_id, amount, reason"
- flag_security   : raise fraud/security alert — value = "user_id, reason"
- ask_user        : ask customer for clarification
- send_response   : send a message to the customer
- escalate        : escalate to specialist — value = "reason, priority (P1/P2)"
- resolve         : CALL THIS when done — ends the episode
- close_no_action : close without action (spam only)

MANDATORY POLICIES (violations cost score):
1. ALWAYS call check_account BEFORE process_refund
2. NEVER process_refund on a chargeback ticket without escalating first
3. NEVER process_refund on a fraud/new-suspicious account — flag_security + escalate instead
4. GDPR requests must NOT be closed — route and escalate
5. Refund abuse accounts (refund_abuse_flag) must be DECLINED, not refunded

DECISION FLOWCHART:
- Duplicate charge?         -> lookup_order -> check_account -> process_refund -> resolve
- Password/login issue?     -> check_account -> search_kb(password) -> send_response -> resolve
- Cancel subscription?      -> check_account -> search_kb(cancel) -> send_response -> resolve
- Late/missing delivery?    -> lookup_order -> send_response -> resolve
- Billing address update?   -> search_kb(billing) -> send_response -> resolve
- Chargeback mentioned?     -> lookup_order -> check_account -> search_kb(chargeback) -> escalate -> resolve
- Fraud / suspicious acct?  -> check_account -> flag_security -> escalate -> resolve  (NO refund!)
- Refund abuse flag?        -> check_account -> search_kb(abuse) -> send_response(decline) -> resolve
- Enterprise / API issue?   -> check_account -> search_kb(enterprise/quota) -> escalate(P1) -> resolve
- GDPR request?             -> check_account -> flag_security -> search_kb(gdpr) -> escalate -> resolve
- Damaged product?          -> lookup_order -> check_account -> search_kb(damaged) -> process_refund -> resolve
- Subscription refund?      -> check_account -> lookup_order -> search_kb(refund) -> process_refund -> resolve
- Bulk/reseller issue?      -> check_account -> search_kb(bulk) -> escalate -> resolve

RULES:
- NEVER repeat an action with the same value you already used
- Call resolve AS SOON AS the required actions are complete
- DO NOT exceed 12 steps

Respond ONLY with valid JSON — no markdown, no explanation:
{"action_type": "<action>", "action_value": "<value>"}"""

# ── ANSI colours ──────────────────────────────────────────────────────────────
def _c(code, t): return f"\033[{code}m{t}\033[0m"
def green(t):  return _c("32", t)
def red(t):    return _c("31", t)
def yellow(t): return _c("33", t)
def cyan(t):   return _c("36", t)
def dim(t):    return _c("2",  t)
def bold(t):   return _c("1",  t)


# ── Logging ───────────────────────────────────────────────────────────────────
def log_start(task, model, ticket, tier, age):
    diff_key = task.split("_")[0]
    colour   = {"easy": green, "med": yellow, "hard": red}.get(diff_key, cyan)
    label    = DIFFICULTY_MAP.get(diff_key, "      ")
    print(); print(colour(f"━━━  {label}  {task}  ━━━"))
    print(f"  {dim('Ticket :')} {cyan(ticket[:120])}")
    print(f"  {dim('Account:')} tier={tier}  age={age}d"); print()

def log_step(step, atype, avalue, reward, done, feedback):
    r_col    = green(f"+{reward:.3f}") if reward > 0 else (red(f"{reward:.3f}") if reward < 0 else dim(f"{reward:.3f}"))
    # val_disp = avalue[:60] + "..." if len(avalue) > 60 else avalue
    val_disp = avalue
    # fb_disp  = feedback[:100] + "..." if len(feedback) > 100 else feedback
    fb_disp = feedback
    print(f"  {dim(f'Step {step:>2})')}  {bold(atype):<20}  val={cyan(val_disp)}")
    print(f"           reward={r_col}  done={str(done).lower()}")
    if fb_disp and "New ticket" not in fb_disp:
        print(f"           {dim('feedback:')} {fb_disp}")
    print()

def log_end(task_id, score, steps, step_rewards, elapsed, violations):
    success = score >= SUCCESS_THRESHOLD
    status  = green("PASS") if success else red("FAIL")
    bar_n   = int(score * 20)
    bar     = green("█" * bar_n) + dim("░" * (20 - bar_n))
    print(f"  Result: {status}  score={bold(f'{score:.4f}')}  [{bar}]")
    print(f"  Steps: {steps}/{MAX_STEPS}   Time: {elapsed:.1f}s")
    if step_rewards:
        print(f"  Step rewards: {', '.join(f'{r:.3f}' for r in step_rewards)}")
    if violations:
        print(f"  {red('Violations:')} {', '.join(violations)}")
    print()
    rewards_str = ",".join(f"{r:.2f}" for r in step_rewards)
    print(f"[END] task={task_id} success={str(success).lower()} steps={steps} score={score:.4f} rewards=[{rewards_str}]", flush=True)

def print_banner(mode):
    print(); print("=" * 66)
    print("         OmniSupportEnv - Baseline Agent Evaluation")
    print("=" * 66)
    print(f"  Model  : {MODEL_NAME}")
    print(f"  Mode   : {bold(green('LOCAL')) if mode == 'local' else bold(cyan('REMOTE'))} ({'no HF space needed' if mode == 'local' else HF_SPACE_URL})")
    print(f"  Tasks  : {len(TASK_IDS)} tickets (5 easy . 5 medium . 5 hard)")
    print(f"  Max steps/episode: {MAX_STEPS}"); print()

# def print_summary(scores, task_ids, elapsed_total):
#     print("\n" + "=" * 66)
#     print("                       FINAL SUMMARY")
#     print("=" * 66)
#     groups = {"easy": [], "med": [], "hard": []}
#     for tid, sc in zip(task_ids, scores):
#         groups.setdefault(tid.split("_")[0], []).append(sc)
#     for label, key in [("Easy   (5)", "easy"), ("Medium (5)", "med"), ("Hard   (5)", "hard")]:
#         grp = groups.get(key, [])
#         if not grp: continue
#         avg    = sum(grp) / len(grp)
#         passed = sum(1 for s in grp if s >= SUCCESS_THRESHOLD)
#         bar    = "█" * int(avg * 20) + "░" * (20 - int(avg * 20))
#         print(f"  {label}:  avg={avg:.4f}  [{bar}]  pass={passed}/{len(grp)}")
#     overall    = sum(scores) / len(scores) if scores else 0.0
#     total_pass = sum(1 for s in scores if s >= SUCCESS_THRESHOLD)
#     print(f"\n  Overall avg  : {bold(f'{overall:.4f}')}")
#     print(f"  Tasks passed : {total_pass}/{len(scores)}   Time: {elapsed_total:.1f}s\n")
#     print(dim("  Task                              Score    Status"))
#     print(dim("  " + "-" * 48))
#     for tid, sc in zip(task_ids, scores):
#         status = green("PASS") if sc >= SUCCESS_THRESHOLD else red("FAIL")
#         colour = {"easy": green, "med": yellow, "hard": red}.get(tid.split("_")[0], cyan)
#         print(f"  {colour(tid):<36} {sc:.4f}   {status}")
#     print()
#     avg_by_diff = {k: (sum(v)/len(v) if v else 0.0) for k, v in groups.items()}
#     print(f"[SUMMARY] tasks={len(task_ids)} avg_score={overall:.4f} passed={total_pass}/{len(scores)} "
#           f"easy_avg={avg_by_diff.get('easy',0):.4f} med_avg={avg_by_diff.get('med',0):.4f} hard_avg={avg_by_diff.get('hard',0):.4f}", flush=True)

def print_summary(scores, task_ids, elapsed_total):
    print("\n" + "=" * 66)
    print("                       FINAL SUMMARY")
    print("=" * 66)

    groups = {"easy": [], "med": [], "hard": []}

    for tid, sc in zip(task_ids, scores):
        key = tid.split("_")[0]
        groups.setdefault(key, []).append(sc)

    # Per-difficulty breakdown
    for label, key in [("Easy   (5)", "easy"),
                       ("Medium (5)", "med"),
                       ("Hard   (5)", "hard")]:

        grp = groups.get(key, [])
        if not grp:
            continue

        avg = sum(grp) / len(grp)
        passed = sum(1 for s in grp if s >= SUCCESS_THRESHOLD)
        bar = "█" * int(avg * 20) + "░" * (20 - int(avg * 20))

        print(f"  {label}:  avg={avg:.4f}  [{bar}]  pass={passed}/{len(grp)}")

    # Overall stats
    overall = sum(scores) / len(scores) if scores else 0.0
    total_pass = sum(1 for s in scores if s >= SUCCESS_THRESHOLD)

    print(f"\n  Overall avg  : {bold(f'{overall:.4f}')}")
    print(f"  Tasks passed : {total_pass}/{len(scores)}   Time: {elapsed_total:.1f}s\n")

    print(dim("  Task                              Score    Status"))
    print(dim("  " + "-" * 48))

    for tid, sc in zip(task_ids, scores):
        status = green("PASS") if sc >= SUCCESS_THRESHOLD else red("FAIL")
        colour = {"easy": green, "med": yellow, "hard": red}.get(tid.split("_")[0], cyan)
        print(f"  {colour(tid):<36} {sc:.4f}   {status}")

    print()

    # Compute averages safely
    avg_by_diff = {
        k: (sum(v) / len(v) if v else 0.0)
        for k, v in groups.items()
    }

    # Build summary dynamically (NO fake values)
    parts = [
        f"tasks={len(task_ids)}",
        f"avg_score={overall:.4f}",
        f"passed={total_pass}/{len(scores)}"
    ]

    # Only include if group actually exists
    if groups.get("easy"):
        parts.append(f"easy_avg={avg_by_diff['easy']:.4f}")
    if groups.get("med"):
        parts.append(f"med_avg={avg_by_diff['med']:.4f}")
    if groups.get("hard"):
        parts.append(f"hard_avg={avg_by_diff['hard']:.4f}")

    print(f"[SUMMARY] {' '.join(parts)}", flush=True)


# ── LLM helpers ───────────────────────────────────────────────────────────────
def parse_action(text):
    text = text.strip()
    if "```" in text:
        text = "\n".join(l for l in text.splitlines() if not l.startswith("```")).strip()
    try:
        data = json.loads(text)
        return str(data.get("action_type", "resolve")), str(data.get("action_value", "done"))
    except Exception:
        s = text.find("{"); e = text.rfind("}") + 1
        if s != -1 and e > s:
            try:
                data = json.loads(text[s:e])
                return str(data.get("action_type", "resolve")), str(data.get("action_value", "done"))
            except Exception: pass
    return "resolve", "parse_error"

def format_obs(obs):
    ticket  = getattr(obs, "ticket_text",         "")
    user_id = getattr(obs, "user_id",              "")
    tier    = getattr(obs, "account_tier",         "free")
    age     = getattr(obs, "account_age_days",      0)
    step    = getattr(obs, "step_number",           0)
    remain  = getattr(obs, "steps_remaining",       0)
    results = getattr(obs, "tool_results",         [])
    viols   = getattr(obs, "policy_violations",    [])
    fb      = getattr(obs, "last_feedback",        "")
    cum_r   = getattr(obs, "cumulative_reward",    0.0)
    history = getattr(obs, "conversation_history", [])

    parts = [
        "=== SUPPORT TICKET ===", f"Customer message: {ticket}", "",
        "=== ACCOUNT CONTEXT (use these exact values) ===",
        f"user_id      : {user_id}", f"account_tier : {tier}", f"account_age  : {age} days", "",
        f"Step {step} | Steps remaining: {remain} | Cumulative reward: {cum_r:.3f}",
    ]
    actions = [m["content"] for m in history if m.get("role") == "assistant" and m.get("content", "").startswith("[")]
    if actions:
        parts.append("\n=== ACTIONS TAKEN SO FAR ===")
        parts.extend(f"  {a}" for a in actions[-6:])
    if results:
        parts.append("\n=== TOOL RESULTS ===")
        for r in results[-3:]:
            parts.append(json.dumps(r, default=str)[:400])
    if viols:
        parts.append("\n=== POLICY VIOLATIONS - FIX THESE ===")
        for v in viols: parts.append(f"  VIOLATION: {v}")
    if fb and "New ticket" not in fb:
        parts.append(f"\nLast action result: {fb[:200]}")
    parts += ["", "=== INSTRUCTIONS ===",
              "- Use the user_id and order IDs shown ABOVE — do NOT invent values",
              "- Do NOT repeat actions you already took",
              "- Call resolve when you have completed the necessary steps",
              "", "Next action (JSON only):"]
    return "\n".join(parts)

def get_action(client, prompt):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user",   "content": prompt}],
            temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
        )
        return parse_action(resp.choices[0].message.content or "")
    except Exception as e:
        print(red(f"  [LLM ERROR] {e}"), flush=True)
        return "resolve", "llm_error"


# ═════════════════════════════════════════════════════════════════════════════
# LOCAL ENV WRAPPER  (no HTTP needed)
# ═════════════════════════════════════════════════════════════════════════════
class LocalEnvClient:
    """Wraps OmniSupportEnvironment directly — no HF Space required."""
    def __init__(self):
        # Add server/ to path so imports inside environment.py work
        server_dir = os.path.join(os.path.dirname(__file__), "server")
        if server_dir not in sys.path:
            sys.path.insert(0, server_dir)
        from environment import OmniSupportEnvironment
        self._env = OmniSupportEnvironment()

    def reset(self, task_id=None):
        return self._env.reset(task_id=task_id)

    def step(self, action):
        return self._env.step(action)

    def close(self): pass   # nothing to close


# ═════════════════════════════════════════════════════════════════════════════
# HTTP ENV CLIENT  (calls HF Space)
# ═════════════════════════════════════════════════════════════════════════════
class HttpEnvClient:
    def __init__(self, base_url):
        import httpx
        self._url  = base_url.rstrip("/")
        self._http = httpx.Client(timeout=45.0)   # sync client — no async needed

    def reset(self, task_id=None):
        try:
            payload = {"task_id": task_id} if task_id else {}
            r = self._http.post(f"{self._url}/reset", json=payload)
            r.raise_for_status()
            return _wrap(r.json())
        except Exception as e:
            print(red(f"  [ERROR] reset failed: {e}"), flush=True)
            return _safe_result()

    def step(self, action):
        try:
            payload = {"action": {"action_type": action.action_type.value,
                                  "action_value": action.action_value}}
            r = self._http.post(f"{self._url}/step", json=payload)
            r.raise_for_status()
            return _wrap(r.json())
        except Exception as e:
            print(red(f"  [ERROR] step failed: {e}"), flush=True)
            return _safe_result(done=True)

    def close(self):
        try: self._http.close()
        except Exception: pass


class _Obs:
    def __init__(self, d): self.__dict__.update(d)

class _Result:
    def __init__(self, data):
        raw = data.get("observation", data)   # local env returns obs directly; HTTP wraps it
        self.observation = raw if isinstance(raw, _Obs) else _Obs(raw if isinstance(raw, dict) else {})
        self.reward = data.get("reward", 0.0) if isinstance(data, dict) else 0.0
        self.done   = data.get("done",   False) if isinstance(data, dict) else False

def _wrap(data):       return _Result(data)
def _safe_result(done=False): return _Result({"observation": {}, "reward": 0.0, "done": done})


# ── Adapter: make local env look like HttpEnvClient ───────────────────────────
class LocalResultAdapter:
    """Converts SupportObservation (from local env) into the same shape as _Result."""
    def __init__(self, obs):
        self.observation = obs   # already a proper object with attributes
        self.reward      = getattr(obs, "reward", 0.0)
        self.done        = getattr(obs, "done",   False)


# ═════════════════════════════════════════════════════════════════════════════
# EPISODE RUNNER  (works with both local and HTTP env)
# ═════════════════════════════════════════════════════════════════════════════
def run_task(env, client, task_id, index, total, use_local):
    server_dir = os.path.join(os.path.dirname(__file__), "server")
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)
    from models import SupportAction, ActionType

    step_rewards   = []
    all_violations = []
    steps_taken    = 0
    final_score    = 0.0
    t0 = time.time()

    # ── reset ──────────────────────────────────────────────────────────────
    raw = env.reset(task_id=task_id)
    result = LocalResultAdapter(raw) if use_local else raw

    obs    = result.observation
    ticket = getattr(obs, "ticket_text",        "")
    tier   = getattr(obs, "account_tier",       "")
    age    = getattr(obs, "account_age_days",    0)

    log_start(task_id, MODEL_NAME, ticket, tier, age)
    print(f"[START] task={task_id} env={BENCHMARK} model={MODEL_NAME}", flush=True)

    try:
        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            atype_str, avalue = get_action(client, format_obs(result.observation))

            try:   atype = ActionType(atype_str)
            except ValueError: atype = ActionType.RESOLVE

            action = SupportAction(action_type=atype, action_value=avalue)
            raw    = env.step(action)
            result = LocalResultAdapter(raw) if use_local else raw

            reward   = result.reward or 0.0
            done     = result.done
            obs      = result.observation
            feedback = getattr(obs, "last_feedback",     "")
            viols    = getattr(obs, "policy_violations", [])
            all_violations = list(viols)
            steps_taken    = step

            if done:
                final_score = max(0.0, min(1.0, reward))
            else:
                step_rewards.append(reward)

            log_step(step, atype_str, avalue, reward, done, feedback)
            print(f"[STEP] step={step} action={atype_str}:{avalue[:40]} reward={reward:.3f} done={str(done).lower()}", flush=True)

            if done:
                break

    except Exception as e:
        print(red(f"  [RUN ERROR] {e}"), flush=True)
        import traceback; traceback.print_exc()

    elapsed = time.time() - t0
    log_end(task_id, final_score, steps_taken, step_rewards, elapsed, all_violations)
    return final_score


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main():
    global MODEL_NAME, HF_SPACE_URL
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("tasks", nargs="*", help="task IDs to run (default: all 15)")
    p.add_argument("--url",   default=None, help="force HTTP mode with this HF Space URL")
    p.add_argument("--model", default=None, help="override MODEL_NAME")
    args = p.parse_args()

    if args.model:
        MODEL_NAME = args.model
    if args.url:
        HF_SPACE_URL = args.url

    use_local = USE_LOCAL

    # --url forces HTTP mode; otherwise auto-fallback logic runs
    if args.url:
        use_local = False
    elif not use_local:
        try:
            import httpx
            r = httpx.get(f"{HF_SPACE_URL}/health", timeout=8.0)
            if r.status_code not in (200, 405):
                print(yellow(f"  [WARN] HF Space returned {r.status_code} — switching to LOCAL mode"), flush=True)
                use_local = True
        except Exception as e:
            print(yellow(f"  [WARN] HF Space unreachable ({e}) — switching to LOCAL mode"), flush=True)
            use_local = True

    print_banner("local" if use_local else "remote")

    if use_local:
        env = LocalEnvClient()
    else:
        env = HttpEnvClient(HF_SPACE_URL)

    client  = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")
    scores  = []
    run_ids = []
    t_start = time.time()

    tasks = args.tasks if args.tasks else TASK_IDS

    try:
        for i, task_id in enumerate(tasks, 1):
            score = run_task(env, client, task_id, i, len(tasks), use_local)
            scores.append(score)
            run_ids.append(task_id)
            if i < len(tasks):
                time.sleep(1)
    finally:
        env.close()

    print_summary(scores, run_ids, time.time() - t_start)


if __name__ == "__main__":
    main()