---
title: OmniSupportEnv
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# OmniSupportEnv

> **A multi-step Reinforcement Learning environment where an AI agent handles real enterprise customer support tickets — using tools, enforcing company policy, and resolving issues across 15 hand-crafted scenarios.**

Built for the **Meta PyTorch × Scaler OpenEnv Hackathon — Round 1** using the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) framework.

**Live Space:** `https://shraddhashaha-omni-support-env.hf.space`

---

## Why This Problem

Every large company employs thousands of support agents to handle billing disputes, fraud alerts, technical issues, and compliance requests. An AI that can navigate these scenarios reliably — using the right tools, following policy, and reaching correct resolutions — would have immediate real-world value.

This environment trains and evaluates exactly that agent. It is not a game or toy problem. Every task maps directly to a workflow that exists in production customer operations systems today.

---

## What the Agent Does

Each episode is one support ticket. The agent receives the ticket text, customer profile, and account context. It then takes a sequence of actions — calling tools, asking questions, enforcing policy — to resolve the ticket within 15 steps.

```
reset()  →  ticket arrives: "I was charged twice for order #78234..."

step("check_account: USR_4821")     →  account is clean, premium tier    +reward
step("lookup_order: 78234")         →  duplicate charge confirmed         +reward
step("process_refund: 78234,49.99") →  refund initiated                   +reward
step("resolve: duplicate refunded") →  episode ends, final score computed
```

The agent earns reward throughout the episode (dense signal), not just at the end.

---

## Architecture

```
omni-support-env/
│
├── inference.py          ← Baseline script: runs LLM agent, emits [START][STEP][END] logs
├── client.py             ← HTTP client: connects to live HF Space, no Docker needed
├── models.py             ← Typed Pydantic models: Action, Observation, State
├── openenv.yaml          ← OpenEnv manifest: name, version, tags, sdk, port
├── pyproject.toml        ← Python project config + entrypoint
├── requirements-docker.txt ← Production dependencies for Docker
├── Dockerfile            ← Root-level Dockerfile (HF Space deployment)
│
└── server/
    ├── app.py            ← FastAPI app: wraps environment with OpenEnv server
    ├── environment.py    ← Core logic: reset(), step(), policy checks, reward dispatch
    ├── tasks.py          ← 15 hand-crafted tickets + deterministic tool response data
    ├── tools.py          ← 8 tool implementations: search_kb, lookup_order, etc.
    ├── reward.py         ← Dense reward engine: step reward + episode reward
    └── graders.py        ← 3-tier graders: grade_easy, grade_medium, grade_hard
```

### How the Files Connect

```
inference.py
    └── client.py  ──────────────────────────────────► HF Space (REST API)
                                                              │
                                                         server/app.py
                                                              │
                                                    server/environment.py
                                                    ┌─────────┼──────────┐
                                               tasks.py   tools.py    reward.py
                                                                          │
                                                                      graders.py
                                                                          │
                                                                      models.py
```

One agent action flows like this:

1. `inference.py` calls `client.step(action)`
2. `client.py` sends `POST /step` to the live HF Space
3. `server/app.py` routes it to `environment.step()`
4. `environment.py` calls `execute_tool()` from `tools.py`
5. Tool returns a deterministic response from `tasks.py`
6. `reward.py` computes the per-step reward
7. If `done=True`, `graders.py` computes the final episode score
8. `SupportObservation` is returned all the way back to `inference.py`
9. `inference.py` prints the `[STEP]` log line

---

## Action Space

The agent picks one action type per step and provides a free-text value.

| action_type      | action_value format               | What it does                        |
|------------------|-----------------------------------|-------------------------------------|
| `search_kb`      | `"refund policy"`                 | Search internal knowledge base      |
| `lookup_order`   | `"78234"`                         | Get order status, amount, flags     |
| `check_account`  | `"USR_4821"`                      | Get account tier, risk score, flags |
| `process_refund` | `"78234, 49.99, duplicate charge"`| Issue a refund (CSV format)         |
| `flag_security`  | `"USR_9901, suspected fraud"`     | Raise security alert on account     |
| `ask_user`       | `"Can you confirm order number?"` | Ask the customer a question         |
| `send_response`  | `"Your refund has been processed"`| Send a message to the customer      |
| `escalate`       | `"Chargeback needs specialist"`   | Escalate to specialist team         |
| `resolve`        | `"Issue resolved, ticket closed"` | Mark ticket resolved — ends episode |
| `close_no_action`| `"Spam ticket"`                   | Close without action — ends episode |

---

## Observation Space

After every step the agent sees a `SupportObservation` containing:

| Field                  | Type            | Description                                    |
|------------------------|-----------------|------------------------------------------------|
| `ticket_id`            | str             | Unique ticket identifier                       |
| `ticket_text`          | str             | The original customer message (never changes)  |
| `user_id`              | str             | Customer account ID                            |
| `account_tier`         | str             | `free` / `premium` / `enterprise`              |
| `account_age_days`     | int             | How old the account is (fraud signal)          |
| `conversation_history` | List[dict]      | Full message history so far                    |
| `tool_results`         | List[dict]      | Results returned by every tool called so far   |
| `policy_violations`    | List[str]       | Policies breached so far this episode          |
| `resolved`             | bool            | Whether a resolution action was taken          |
| `step_number`          | int             | Current step (1-indexed)                       |
| `steps_remaining`      | int             | Steps left before forced termination           |
| `last_feedback`        | str             | Plain-English feedback on last action          |
| `cumulative_reward`    | float           | Total reward accumulated so far                |
| `done`                 | bool            | Whether the episode has ended                  |
| `reward`               | float or None   | Reward from the last action                    |

---

## Tasks — 15 Scenarios Across 3 Difficulty Levels

### Easy (5 tasks) — Score range: 0.65–0.85
Clear single-intent tickets. 1–2 tools needed. A well-prompted LLM should handle these cleanly.

| Task ID                  | Scenario                    | Required Tools                    |
|--------------------------|-----------------------------|-----------------------------------|
| `easy_refund_001`        | Duplicate charge refund     | `check_account`, `process_refund` |
| `easy_password_001`      | Account locked              | `check_account`, `search_kb`      |
| `easy_cancel_001`        | Subscription cancellation   | `check_account`                   |
| `easy_delivery_001`      | Missing delivery            | `lookup_order`                    |
| `easy_update_001`        | Billing address update      | `search_kb`                       |

### Medium (5 tasks) — Score range: 0.40–0.65
Ambiguous tickets requiring multiple tools and policy judgment. Agent must investigate before acting.

| Task ID                       | Scenario                        | Key Challenge                              |
|-------------------------------|---------------------------------|--------------------------------------------|
| `med_chargeback_001`          | Chargeback + delivery dispute   | Must escalate before refunding             |
| `med_partial_refund_001`      | Damaged goods, keep item        | Must verify with photo evidence policy     |
| `med_tech_billing_001`        | App crash + billing credit      | Technical + billing cross-over             |
| `med_subscription_dispute_001`| Cancelled but still charged     | Must verify cancellation record first      |
| `med_api_quota_001`           | Enterprise quota exceeded       | SLA-bound P1 escalation required           |

### Hard (5 tasks) — Score range: 0.20–0.40
Fraud signals, policy traps, multi-issue tickets. Even frontier models struggle here.

| Task ID                      | Scenario                     | Trap                                          |
|------------------------------|------------------------------|-----------------------------------------------|
| `hard_fraud_001`             | 3 unauthorised transactions  | Must flag security BEFORE refunding — new account with risk_score 0.87 |
| `hard_abuse_001`             | 4 refund requests in 90 days | Must decline — refund abuse policy             |
| `hard_enterprise_breach_001` | Compromised API key          | Security incident + audit + escalation all required |
| `hard_bulk_001`              | 12 accounts, bulk refunds    | Cannot process individually — must escalate  |
| `hard_gdpr_001`              | GDPR + hack + refund in one  | Must triage into separate tickets, not delete blindly |

---

## Reward Design

### Step Reward (dense — fires every action)

The agent receives signal on every single action, not just at the end. This makes learning faster.

| Condition                                    | Reward  |
|----------------------------------------------|---------|
| First use of a required tool                 | +0.08   |
| Correctly flagging security (fraud tasks)    | +0.12   |
| Correctly escalating when required           | +0.10   |
| Meaningful message to customer               | +0.03   |
| Refunding before security review (trap)      | −0.20   |
| Refunding a serial abuser (trap)             | −0.15   |

### Episode Reward (final — fires at done=True)

Weighted sum of four component scores, each in [0.0, 1.0]:

```
Final Score = resolution(0.40) + tool_use(0.25) + policy(0.20) + efficiency(0.15)
```

| Component      | Weight | What it measures                                      |
|----------------|--------|-------------------------------------------------------|
| Resolution     | 40%    | Correct resolution type + keywords + escalation       |
| Tool use       | 25%    | Coverage of required tools, penalises excess calls    |
| Policy         | 20%    | 1.0 if clean, −0.25 per violation                     |
| Efficiency     | 15%    | Full score if within expected steps, decays after     |

**Hard penalties applied on top:**
- Missed mandatory security flag on fraud task: score × 0.30
- Fell into refund trap: score × 0.20

### Policy Engine

These rules are checked deterministically on every action:

| Rule                                     | Violation code                        |
|------------------------------------------|---------------------------------------|
| Refund before checking account           | `REFUND_WITHOUT_ACCOUNT_CHECK`        |
| Refund on new suspicious account         | `REFUND_ON_SUSPICIOUS_NEW_ACCOUNT`    |
| Refund while chargeback is pending       | `REFUND_DURING_CHARGEBACK`            |
| Closing GDPR request without routing     | `GDPR_REQUEST_CLOSED_WITHOUT_ROUTING` |

---

## Baseline Scores

Measured using `Qwen/Qwen2.5-72B-Instruct` via HuggingFace router:

| Task                    | Difficulty | Score  |
|-------------------------|------------|--------|
| `easy_refund_001`       | easy       | ~0.74  |
| `med_chargeback_001`    | medium     | ~0.47  |
| `hard_fraud_001`        | hard       | ~0.28  |
| **Average**             |            | ~0.50  |

Good agents score above random (0.0) on hard tasks. Bad agents fall into traps and score near 0.0.

---

## Local Setup

### Prerequisites

- Python 3.11+
- Docker Desktop
- A HuggingFace token (free): https://huggingface.co/settings/tokens

### Install

```bash
git clone https://github.com/shraddhashahaof/omni-support-env
cd omni-support-env

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements-docker.txt
pip install pytest httpx
```

### Run the server locally (no Docker)

```bash
cd server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Test it:

```bash
curl http://localhost:8000/health
# {"status":"healthy"}

curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{}'

curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action":{"action_type":"check_account","action_value":"USR_4821"}}'
```

### Run the tests

```bash
python test_phase1.py   # models, reset(), stub step()
python test_phase2.py   # 15 tasks, 6 tools, tool router
python test_phase3.py   # reward components, step rewards, traps
python test_phase4.py   # full episodes, policy checks, score ordering
```

Expected output for all four:
```
✅ ALL PHASE X TESTS PASSED
```

---

## Docker

### Build

```bash
docker build -t omni-support-env:latest -f server/Dockerfile .
```

### Run

```bash
docker run -d --name omni-test -p 7860:7860 omni-support-env:latest
sleep 8
curl http://localhost:7860/health
# {"status":"healthy"}
```

### Stop

```bash
docker stop omni-test && docker rm omni-test
```

---

## Running the Inference Script

The inference script runs the LLM agent against all 3 tasks and produces the mandatory evaluation logs.

### Environment variables

```bash
# Required
HF_TOKEN=hf_your_token_here

# Optional (defaults shown)
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
LOCAL_IMAGE_NAME=omni-support-env:latest
```

Create a `.env` file in the project root with the above, then:

```bash
pip install httpx python-dotenv openai
python inference.py
```

### Expected output format

```
[INFO] Model:  Qwen/Qwen2.5-72B-Instruct
[INFO] Tasks:  ['easy_refund_001', 'med_chargeback_001', 'hard_fraud_001']

[START] task=easy_refund_001 env=omni_support_env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=check_account:USR_4821 reward=0.00 done=false error=null
[STEP] step=2 action=lookup_order:78234 reward=0.08 done=false error=null
[STEP] step=3 action=process_refund:78234,49.99,duplicate reward=0.08 done=false error=null
[STEP] step=4 action=resolve:duplicate charge refunded reward=0.58 done=true error=null
[END] success=true steps=4 score=0.74 rewards=0.00,0.08,0.08,0.58

[START] task=med_chargeback_001 env=omni_support_env model=Qwen/Qwen2.5-72B-Instruct
...
[END] success=false steps=8 score=0.47 rewards=...

[SUMMARY] tasks=3 avg_score=0.4967
```

The inference script connects directly to the live HF Space — no local Docker required.

---

## Deployment

The environment is deployed as a Docker-based HuggingFace Space.

```bash
pip install huggingface_hub
python -m huggingface_hub.commands.huggingface_cli login

openenv push --repo-id shraddhashaha/omni-support-env
```

Live URL: `https://shraddhashaha-omni-support-env.hf.space`

Verify:
```bash
curl https://shraddhashaha-omni-support-env.hf.space/health
# {"status":"healthy"}
```

---

## API Endpoints

Once running (locally or on HF Spaces):

| Endpoint  | Method | Description                              |
|-----------|--------|------------------------------------------|
| `/health` | GET    | Returns `{"status":"healthy"}`           |
| `/reset`  | POST   | Start a new episode, returns observation |
| `/step`   | POST   | Execute one action, returns observation + reward |
| `/state`  | GET    | Returns current internal episode state   |
| `/docs`   | GET    | Interactive API docs (Swagger UI)        |

### Reset with specific task

```json
POST /reset
{"task_id": "hard_fraud_001"}
```

### Step payload

```json
POST /step
{
  "action": {
    "action_type": "check_account",
    "action_value": "USR_9901"
  }
}
```

---

## OpenEnv Compliance

This environment fully implements the OpenEnv specification:

- Typed `Action`, `Observation`, `State` models via Pydantic v2
- `reset()` → returns initial `SupportObservation`
- `step(action)` → returns `(observation, reward, done)`
- `state` property → returns `SupportState`
- `openenv.yaml` with correct metadata and tags
- Passes `openenv validate`
- Deployed as Docker-based HuggingFace Space on port 7860
- Tagged with `openenv` for hub discovery

---

## Project Info

**Hackathon:** Meta PyTorch × Scaler OpenEnv Round 1  
**Team:** Solo — Shraddha Shaha [AgentOne] 
**Domain:** Customer Operations / Enterprise Support  
**Framework:** OpenEnv v0.2.3  
**Model tested:** Qwen/Qwen2.5-72B-Instruct  
**GitHub:** https://github.com/shraddhashahaof/omni-support-env  
**HF Space:** https://huggingface.co/spaces/shraddhashaha/omni-support-env