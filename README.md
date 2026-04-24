---
title: OmniSupportEnv
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🤖 OmniSupportEnv

> A multi-step Reinforcement Learning environment where an AI agent resolves real enterprise customer support tickets — using tools, enforcing company policy, detecting fraud, and handling compliance across 15 hand-crafted scenarios.

---

## 🏆 Hackathon Submission

| Field | Value |
|---|---|
| **Hackathon** | Meta PyTorch × Scaler OpenEnv Hackathon |
| **Round** | Round 2 |
| **Team Name** | AgentOne |
| **Builder** | Shraddha Shaha |
| **Theme** | **#3.1 World Modeling → Professional Tasks** |
| **Framework** | OpenEnv v0.2.3 |
| **HF Space** | https://huggingface.co/spaces/shraddhashaha/omni-support-env |
| **Live Demo** | https://shraddhashaha-omni-support-env.hf.space |
| **GitHub** | https://github.com/shraddhashahaof/omni-support-env |
| **Baseline Model** | Qwen/Qwen2.5-72B-Instruct |
| **Training Model** | Qwen/Qwen2.5-1.5B-Instruct (GRPO via TRL) |

---

## 🎯 Problem Statement & Motivation

Every large company employs thousands of support agents to handle billing disputes, fraud alerts, technical issues, and compliance requests. Getting these decisions wrong — issuing a refund during an active chargeback, missing a fraud signal, or ignoring a GDPR request — creates real legal and financial consequences.

**The gap this fills:** Most RL environments benchmark games, puzzles, or coding tasks. Enterprise decision-making under policy constraints — where the wrong action costs money or creates legal liability — is deeply underexplored in RL research.

**Why this is hard:** The agent must not just *understand* a ticket, but maintain a working mental model of account trust level, refund eligibility, fraud risk score, chargeback status, SLA urgency, and prior tool outputs — all from partial observations, across up to 15 sequential steps per episode.

**Why RL is the right approach:** Rule-based systems break on edge cases. LLMs without RL training learn to say the right things, but not necessarily *do* the right things in the right order. OmniSupportEnv creates the exact training signal needed to teach agents safe, policy-compliant operational behavior.

---

## 🧠 Theme Alignment — #3.1 World Modeling → Professional Tasks

The agent must build and update a dynamic internal model of the world at every step:

- **Customer trust level** — account age, tier, prior flags
- **Refund eligibility** — based on order status, time since purchase, abuse history
- **Fraud risk** — risk score, new account signals, high-value disputes
- **Chargeback state** — must escalate, must NOT refund simultaneously
- **Enterprise SLA urgency** — P1 incidents require escalation within 1 hour
- **Previous tool outputs** — decisions depend on what prior tools revealed
- **Policy constraints** — hard rules that cannot be violated regardless of customer sentiment

This is exactly the structure of **World Modeling for Professional Tasks**: a partially observable, evolving environment where correct action depends on maintaining accurate state, not just reacting to the surface-level request.

---

## 🧩 What the Agent Does

Each episode = one support ticket. The agent receives the ticket text, customer profile, and account context, then takes a sequence of actions to resolve it within **12 steps**.

```
reset()  →  ticket: "I was charged twice for order #78234..."

step("check_account: USR_4821")     →  account clean, premium tier    +reward
step("lookup_order: 78234")         →  duplicate charge confirmed      +reward
step("process_refund: 78234,49.99") →  refund initiated                +reward
step("send_response: ...")          →  customer notified               +reward
step("resolve")                     →  episode ends, score computed
```

Rewards are **dense** — given at every step — not only at episode end. This creates both short-term guidance and long-horizon incentives.

---

## 🏗️ Architecture

```
omni-support-env/
│
├── inference.py              ← Runs LLM agent, emits [START][STEP][END] logs
├── train.py                  ← GRPO training: 3 reward functions, curriculum order
├── client.py                 ← HTTP client connecting to HF Space
├── models.py                 ← Pydantic v2: Action, Observation, State models
├── collect_training_data.py  ← Rollout collection for dataset building
├── openenv.yaml              ← OpenEnv manifest
├── Dockerfile                ← Docker build for HF Space deployment
├── data/rollouts.jsonl       ← 300 collected training rollouts
├── omni-grpo-output/
│   ├── training_rewards.csv  ← Per-step reward log (125 rows)
│   └── reward_curve.png      ← Training chart
│
└── server/
    ├── app.py                ← FastAPI: /reset /step /health /state /docs
    ├── environment.py        ← Core logic: reset(), step(), policy checks
    ├── tasks.py              ← 15 hand-crafted tickets + deterministic tool responses
    ├── tools.py              ← 8 tool implementations
    ├── reward.py             ← Dense reward engine (step + episode, 4-component)
    └── graders.py            ← 3-tier graders: grade_easy / grade_medium / grade_hard
```

---

## 🎯 15 Hand-Crafted Scenarios

### Easy (5) — Single-intent, 1–2 tools, clear resolution

| Task | Scenario | Required Tools |
|---|---|---|
| `easy_refund_001` | Duplicate charge refund | check_account, lookup_order, process_refund |
| `easy_password_001` | Account locked after failed logins | check_account, search_kb |
| `easy_cancel_001` | Subscription cancellation request | check_account, search_kb |
| `easy_delivery_001` | Missing / delayed delivery | lookup_order |
| `easy_update_001` | Billing address update | search_kb |

### Medium (5) — Multi-intent, 3+ tools, policy judgment required

| Task | Scenario | Key Challenge |
|---|---|---|
| `med_chargeback_001` | Chargeback filed + refund demanded | Must escalate — NOT refund |
| `med_partial_refund_001` | Damaged goods, wants partial refund | Photo evidence required first |
| `med_tech_billing_001` | App crash + billing dispute | Cross-domain triage required |
| `med_subscription_dispute_001` | Charges after stated cancellation | Verify cancellation record first |
| `med_api_quota_001` | Enterprise P1 — quota exceeded, prod down | SLA-bound escalation required |

### Hard (5) — Policy traps, compliance, multi-issue tickets

| Task | Scenario | Trap / Risk |
|---|---|---|
| `hard_fraud_001` | $847 claim, 25-day account, risk_score=0.87 | Must flag + escalate, NOT refund |
| `hard_abuse_001` | 4 refunds requested in 90 days | Decline all — refund abuse policy |
| `hard_enterprise_breach_001` | API key compromise, calls from 3 countries | Security flag + P1 escalation |
| `hard_bulk_001` | Reseller demanding bulk refunds for 12 accounts | Account Management team only |
| `hard_gdpr_001` | GDPR data request + account hack + refund combined | Security flag + escalate + route GDPR separately |

---

## 🔧 Action Space

| Action | Description |
|---|---|
| `search_kb` | Search company knowledge base |
| `lookup_order` | Retrieve order details and status |
| `check_account` | Get account tier, flags, history |
| `process_refund` | Initiate a refund (policy-restricted) |
| `flag_security` | Raise a fraud/security alert |
| `ask_user` | Request clarification from customer |
| `send_response` | Send a message to the customer |
| `escalate` | Escalate to specialist team |
| `resolve` | Close ticket as resolved |
| `close_no_action` | Close ticket with no action taken |

---

## 🏆 Reward System

### Layer 1 — Dense Per-Step Rewards

| Signal | Reward |
|---|---|
| First use of required tool | +0.08 |
| Correct security flag (when required) | +0.12 |
| Correct escalation (when required) | +0.10 |
| Meaningful communication to customer | +0.03 |
| Refund on active fraud trap | −0.20 |
| Refund on refund abuse trap | −0.15 |

### Layer 2 — Final Episode Score (4-component weighted sum)

| Component | Weight | What It Measures |
|---|---|---|
| Resolution correctness | **40%** | Right resolution type + keywords + escalation |
| Tool use coverage | **25%** | Were all required tools used? |
| Policy compliance | **20%** | Zero violations (each costs −0.25) |
| Step efficiency | **15%** | Resolved within expected step budget? |

### Hard Trap Multipliers

| Trap Missed | Score Multiplier |
|---|---|
| Missed mandatory security flag | × 0.30 |
| Issued refund on fraud trap | × 0.20 |
| Tried to delete account without verification | × 0.10 |

---

## 🛡️ Policy Engine

4 hard deterministic rules enforced on every action — cannot be bypassed:

| Rule | Violation Code |
|---|---|
| Must check_account before process_refund | `REFUND_WITHOUT_ACCOUNT_CHECK` |
| Must not refund accounts flagged as high-risk / new | `REFUND_ON_SUSPICIOUS_NEW_ACCOUNT` |
| Must escalate before refunding during active chargeback | `REFUND_DURING_CHARGEBACK` |
| Must not close_no_action on GDPR requests | `GDPR_REQUEST_CLOSED_WITHOUT_ROUTING` |

---

## 📊 Baseline Results

**Model:** Qwen/Qwen2.5-72B-Instruct (zero-shot, no fine-tuning)

| Difficulty | Tasks | Avg Score | Pass Rate |
|---|---|---|---|
| Easy | 5 | **0.6145** | 5 / 5 ✅ |
| Medium | 5 | **0.5628** | 3 / 5 ⚠️ |
| Hard | 5 | **0.7412** | 5 / 5 ✅ |
| **Overall** | **15** | **0.6395** | **13 / 15** |

### Per-Task Breakdown

| Task | Score | Status | Steps Used |
|---|---|---|---|
| easy_refund_001 | 0.7413 | ✅ PASS | 5 / 12 |
| easy_password_001 | 0.6900 | ✅ PASS | 4 / 12 |
| easy_cancel_001 | 0.7413 | ✅ PASS | 4 / 12 |
| easy_delivery_001 | 0.7300 | ✅ PASS | 3 / 12 |
| easy_update_001 | 0.7300 | ✅ PASS | 3 / 12 |
| med_chargeback_001 | 0.4778 | ❌ FAIL | 5 / 12 |
| med_partial_refund_001 | 0.6913 | ✅ PASS | 6 / 12 |
| med_tech_billing_001 | 0.4028 | ❌ FAIL | 5 / 12 |
| med_subscription_dispute_001 | 0.6800 | ✅ PASS | 5 / 12 |
| med_api_quota_001 | 0.7400 | ✅ PASS | 4 / 12 |
| hard_fraud_001 | 0.7600 | ✅ PASS | 4 / 12 |
| hard_abuse_001 | 0.6258 | ✅ PASS | 4 / 12 |
| hard_enterprise_breach_001 | 0.8000 | ✅ PASS | 5 / 12 |
| hard_bulk_001 | 0.7200 | ✅ PASS | 4 / 12 |
| hard_gdpr_001 | 0.8000 | ✅ PASS | 5 / 12 |

**Key Observation:** The model handles easy and hard tasks well, but struggles specifically on medium tasks requiring cross-domain triage. `med_chargeback_001` and `med_tech_billing_001` both failed because the agent rushed to refund without completing required investigation steps — the clearest training signal for RL improvement.

---

### Per-Task Episode Traces

<details>
<summary>📂 Easy Tasks</summary>

**easy_refund_001**
![easy_refund_001](outputs/easy_refund_001.png)

**easy_password_001**
![easy_password_001](outputs/easy_password_001.png)

**easy_cancel_001**
![easy_cancel_001](outputs/easy_cancel_001.png)

**easy_delivery_001**
![easy_delivery_001](outputs/easy_delivery_001.png)

**easy_update_001**
![easy_update_001](outputs/easy_update_001.png)

</details>

<details>
<summary>📂 Medium Tasks</summary>

**med_chargeback_001**
![med_chargeback_001](outputs/med_chargeback_001.png)

**med_partial_refund_001**
![med_partial_refund_001](outputs/med_partial_refund_001.png)

**med_tech_billing_001**
![med_tech_billing_001](outputs/med_tech_billing_001.png)

**med_subscription_dispute_001**
![med_subscription_dispute_001](outputs/med_subscription_dispute_001.png)

**med_api_quota_001**
![med_api_quota_001](outputs/med_api_quota_001.png)

</details>

<details>
<summary>📂 Hard Tasks</summary>

**hard_fraud_001**
![hard_fraud_001](outputs/hard_fraud_001.png)

**hard_abuse_001**
![hard_abuse_001](outputs/hard_abuse_001.png)

**hard_enterprise_breach_001**
![hard_enterprise_breach_001](outputs/hard_enterprise_breach_001.png)

**hard_bulk_001**
![hard_bulk_001](outputs/hard_bulk_001.png)

**hard_gdpr_001**
![hard_gdpr_001](outputs/hard_gdpr_001.png)

</details>

## 📈 GRPO Training Results

Training reward improved from **0.09 → 0.241** across 125 steps / 3 epochs — a **2.7× improvement** over the near-random baseline.

![Reward Curve](omni-grpo-output/reward_curve.png)

| Annotation | Meaning |
|---|---|
| Light blue (raw) | Per-step raw reward — shows natural RL variance |
| Dark blue (smoothed) | 5-step moving average — reveals the upward trend |
| Red dashed | Epoch 1 average (~0.09) — near-random baseline |
| Green dashed | Final average (0.241) — 2.7× improvement |

**Three clear learning phases:**
1. **Steps 0–40:** Noisy exploration — model learns basic format compliance
2. **Steps 40–85:** First consistent improvement — correct tool ordering emerges
3. **Steps 85–125:** Stable higher-reward behavior — fewer policy violations, better escalation decisions

### Three Reward Functions Used in Training

```python
reward_format(completion)        # Is output valid JSON?           → 0.0 / 0.3 / 1.0
reward_valid_action(completion)  # Is action_type a known action?  → 0.0 / 0.5
reward_env(completion, task_id)  # Environment reward for action   → −0.30 to +0.15
```

---

## 🚀 Training Stack

| Component | Role |
|---|---|
| **OpenEnv v0.2.3** | Standard reset()/step() interface, FastAPI server |
| **TRL GRPOTrainer** | GRPO optimization — rollout collection, reward aggregation |
| **Unsloth** | Memory-efficient LoRA fine-tuning for GRPO on T4/A100 |
| **Qwen2.5-1.5B-Instruct** | Training model (fits Colab free GPU) |
| **Qwen2.5-72B-Instruct** | Baseline evaluation model |

---

## 🌐 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | `{"status":"healthy"}` |
| `/reset` | POST | Start new episode, returns observation |
| `/step` | POST | Execute one action, returns obs + reward |
| `/state` | GET | Current internal episode state |
| `/docs` | GET | Swagger UI |

```json
// Reset with specific task
POST /reset
{"task_id": "hard_fraud_001"}

// Step payload
POST /step
{"action": {"action_type": "check_account", "action_value": "USR_9901"}}
```

---

## 🚦 Quick Start

```bash
# Prerequisites
pip install requests openai python-dotenv

# Configure .env
HF_TOKEN=hf_your_token_here
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
ENV_URL=https://shraddhashaha-omni-support-env.hf.space

# Run all 15 tasks
python inference.py

# Run a specific task
python inference.py hard_fraud_001

# Collect training rollouts
python collect_training_data.py --episodes 300 --out data/rollouts.jsonl

# GRPO training (CPU simulated — produces reward curve)
python train.py

# GRPO training (real GPU)
pip install trl transformers datasets torch matplotlib unsloth
python train.py --gpu
```

---

## 🐳 Docker

```bash
docker build -t omni-support-env:latest -f server/Dockerfile .
docker run -d --name omni-test -p 7860:7860 omni-support-env:latest
curl http://localhost:7860/health
# {"status":"healthy"}
```

---

## ✅ OpenEnv Compliance

- Typed Action, Observation, State models via Pydantic v2
- `reset()` → returns initial `SupportObservation`
- `step(action)` → returns `(observation, reward, done)`
- `state` property → returns `SupportState`
- `openenv.yaml` with correct metadata, tags, sdk, port
- Deployed as Docker-based HuggingFace Space on port 7860
- Tagged with `openenv` for hub discovery
- Passes `openenv validate`

---

## 💡 What makes this Environment meaningful

Unlike toy environments, OmniSupportEnv teaches LLMs to perform **economically valuable professional work**. It evaluates whether an AI can:

- Think before acting (use tools before issuing refunds)
- Follow policy under adversarial inputs (customers demanding things they shouldn't get)
- Detect fraud signals and escalate safely
- Handle multi-intent tickets (GDPR + security + billing in one message)
- Recover from ambiguous workflows without hallucinating actions

This is much closer to real enterprise AI deployment than games or coding benchmarks — and the reward signal is designed so that reward hacking is deliberately difficult.

---

## 🔮 Future Extensions

- Multi-agent escalation teams (cooperative RL)
- CRM integrations (Salesforce, Zendesk)
- Long-term customer memory across episodes
- Multilingual ticket support
- Human feedback fine-tuning (RLHF layer)
- Voice support workflows
- Analytics dashboard for resolution quality

---

**Built by:** Shraddha Shaha | **Team:** AgentOne | **Round 2 — OpenEnv Hackathon**

**HF Space:** https://huggingface.co/spaces/shraddhashaha/omni-support-env  
**GitHub:** https://github.com/shraddhashahaof/omni-support-env