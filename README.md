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

## Hackathon Submission

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="22%">Field</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Detail</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Hackathon</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Meta PyTorch × Scaler OpenEnv Hackathon — India 2026</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Round</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Round 2 (Onsite)</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Team Name</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">AgentOne</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Builder</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Shraddha Shaha</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Theme</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">#3.1 World Modeling → Professional Tasks</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Framework</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">OpenEnv v0.2.3 + TRL GRPO + Unsloth</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>HF Space</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">https://huggingface.co/spaces/shraddhashaha/omni-support-env</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Live Demo</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">https://shraddhashaha-omni-support-env.hf.space</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>GitHub</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">https://github.com/shraddhashahaof/omni-support-env</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Video / Pitch</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><a href="#">YouTube — 2 min demo</a></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Blog Post</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><a href="#">HuggingFace Blog</a></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Colab Notebook</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><a href="omni_support_training.ipynb">omni_support_training.ipynb</a></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Baseline Model</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Qwen/Qwen2.5-72B-Instruct</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Training Model</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Qwen/Qwen2.5-1.5B-Instruct (GRPO, T4 GPU, 32 min)</td></tr>
</table>

---

## Problem Statement

Every company employs thousands of support agents to handle billing disputes, fraud alerts, and compliance requests. Getting these decisions wrong — refunding during an active chargeback, missing a fraud signal, closing a GDPR ticket — carries real legal and financial consequences.

**The gap this fills:** Enterprise decision-making under strict policy constraints is deeply underexplored in RL research. Most environments benchmark games, puzzles, or code. OmniSupportEnv creates the training signal needed to teach agents safe, policy-compliant, real-world operational behavior.

**Why RL is the right approach:** Rule-based systems break on edge cases. LLMs without RL say the right things but do not do them in the right order. RL trains the agent to maintain a working model of account risk, refund eligibility, fraud status, and SLA urgency — and act correctly across up to 15 sequential steps per episode.

---

## Theme Alignment — #3.1 World Modeling → Professional Tasks

The agent builds and updates an internal world model every step:

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="25%">State Dimension</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">What the agent tracks</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Customer trust</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Account age, tier, prior flags, risk score</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Refund eligibility</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Order status, purchase date, abuse history</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Fraud risk</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Risk score, new account signals, high-value disputes</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Chargeback state</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must escalate first, must NOT refund simultaneously</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">SLA urgency</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Enterprise P1 incidents need escalation within 1 hour</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Tool history</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Decisions depend on what prior tools revealed</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Policy constraints</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Hard rules enforced regardless of customer pressure</td></tr>
</table>

---

## What the Agent Does

Each episode is one support ticket. The agent takes sequential actions to resolve it within 12 steps. Rewards are dense — issued every step, not only at the end.

```
reset()  →  "I was charged twice for order #78234..."

step("check_account: USR_4821")     →  account clean, premium tier      +0.08
step("lookup_order: 78234")         →  duplicate charge confirmed        +0.08
step("process_refund: 78234,49.99") →  refund initiated                  +0.08
step("send_response: ...")          →  customer notified                 +0.03
step("resolve")                     →  episode ends → final score 0.74
```

---

## Architecture

```
omni-support-env/
├── inference.py              ← Multi-agent council + LLM fallback, [START][STEP][END] logs
├── train.py                  ← GRPO training: 4 reward functions, curriculum ordering
├── collect_training_data.py  ← Heuristic rollout collection → JSONL dataset
├── app_streamlit.py          ← Interactive demo dashboard
├── client.py                 ← HTTP client for HF Space
├── models.py                 ← Pydantic v2: Action, Observation, State
├── openenv.yaml              ← OpenEnv manifest
├── Dockerfile                ← HF Space Docker build
│
└── server/
    ├── app.py                ← FastAPI: /reset /step /health /state /docs
    ├── environment.py        ← reset(), step(), 5-rule policy engine
    ├── agents.py             ← Multi-agent specialist council (7 agents)
    ├── tasks.py              ← 15 tickets + deterministic tool responses
    ├── tools.py              ← 8 tool implementations
    ├── reward.py             ← Dense step reward + 4-component episode reward
    └── graders.py            ← Difficulty-tiered graders with trap multipliers
```

---

## 15 Hand-Crafted Scenarios

### Easy (5) — Single-intent, 1–2 tools, clear resolution

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="28%">Task ID</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="36%">Scenario</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Required Tools</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_refund_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Duplicate charge refund</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">check_account, lookup_order, process_refund</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_password_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Account locked after failed logins</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">check_account, search_kb</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_cancel_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Subscription cancellation</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">check_account, search_kb</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_delivery_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Missing or delayed delivery</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">lookup_order</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_update_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Billing address update</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">search_kb</td></tr>
</table>

### Medium (5) — Multi-intent, 3+ tools, policy judgment required

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="28%">Task ID</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="36%">Scenario</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Key Challenge</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_chargeback_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Chargeback filed + refund demanded</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must escalate first — refunding is a policy violation</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_partial_refund_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Damaged goods, wants partial refund</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Photo evidence policy must be cited</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_tech_billing_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">App crash + billing dispute</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Cross-domain triage required</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_subscription_dispute_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Charged after cancellation</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must verify cancellation record first</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_api_quota_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Enterprise P1 — production down</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">SLA-bound P1 escalation required</td></tr>
</table>

### Hard (5) — Policy traps, compliance, adversarial inputs

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="28%">Task ID</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="36%">Scenario</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Trap</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_fraud_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">$847 claim, 25-day account, risk_score=0.87</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must flag + escalate — NOT refund</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_abuse_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 refunds in 90 days, no valid reason</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must decline — refund_abuse_flag active</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_enterprise_breach_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">API key compromised, calls from 3 countries</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Security flag + P1 escalation + audit</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_bulk_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Reseller demanding 12 bulk refunds</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Cannot process individually — Account Management only</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_gdpr_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">GDPR + account hack + refund in one message</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Triage into separate tickets, never close</td></tr>
</table>

---

## 🔧 Action Space

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="22%">Action</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="28%">Value Format</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">What It Does</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>search_kb</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">keyword</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Search internal knowledge base</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>lookup_order</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">order_id</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Get order status, amount, flags</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>check_account</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">user_id</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Get account tier, risk score, flags</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>process_refund</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">order_id, amount, reason</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Issue a refund (policy-gated)</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>flag_security</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">user_id, reason</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Raise fraud or security alert</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>ask_user</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">question</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Request clarification from customer</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>send_response</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">message</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Send message to customer</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>escalate</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">reason, priority</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Escalate to specialist team</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>resolve</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">summary</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Close ticket as resolved — ends episode</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>close_no_action</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">reason</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Close without action (spam only)</td></tr>
</table>

---

## Reward System

### Layer 1 — Dense Per-Step Rewards (every action)

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="60%">Signal</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Reward</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">First use of a required tool</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">+0.08</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Correct security flag on fraud task</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">+0.12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Correct escalation when required</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">+0.10</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Meaningful customer communication</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">+0.03</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Repeat tool call (same type, not needed)</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">−0.03</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Refund before fraud security review</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">−0.25</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Refund on serial abuse account</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">−0.20</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Unnecessary escalation on easy task</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">−0.05</td></tr>
</table>

### Layer 2 — Final Episode Score (4-component weighted sum)

```
Final Score = resolution(0.40) + tool_use(0.25) + policy(0.20) + efficiency(0.15)
```

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="20%">Component</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="12%">Weight</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">What It Measures</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Resolution</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">40%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Correct resolution type + keywords + escalation</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Tool use</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">25%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Coverage of required tools, penalises excess</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Policy</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">20%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">1.0 if clean, −0.35 per violation</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Efficiency</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">15%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Full score within expected steps, decays after</td></tr>
</table>

### Hard Trap Multipliers (applied after weighted sum)

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="65%">Trap Triggered</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Score Multiplier</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Missed mandatory security flag</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">× 0.25</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Refunded during active fraud trap</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">× 0.15</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Refunded abuse-flagged account</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">× 0.10</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Missed required escalation</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">× 0.60</td></tr>
</table>

---

## 🛡️ Policy Engine — 5 Hard Rules

Enforced deterministically on every action. Cannot be bypassed.

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="55%">Rule</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Violation Code</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must call check_account before process_refund</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>REFUND_WITHOUT_ACCOUNT_CHECK</code></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must not refund new high-risk accounts</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>REFUND_ON_SUSPICIOUS_NEW_ACCOUNT</code></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must escalate before refunding during chargeback</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>REFUND_DURING_CHARGEBACK</code></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must not close_no_action on GDPR requests</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>GDPR_REQUEST_CLOSED_WITHOUT_ROUTING</code></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Must not refund accounts with refund_abuse_flag</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>REFUND_ON_ABUSE_FLAGGED_ACCOUNT</code></td></tr>
</table>

---

## 📊 Baseline Results

**Model:** Qwen/Qwen2.5-72B-Instruct — zero-shot, no fine-tuning

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="20%">Difficulty</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="15%">Tasks</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="20%">Avg Score</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Pass Rate</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Easy</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7265</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 5 ✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Medium</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.5904</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">3 / 5 ⚠️</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Hard</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7412</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 5 ✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Overall</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>15</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>0.6860</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>13 / 15</b></td></tr>
</table>

### Per-Task Breakdown

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="34%">Task</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="15%">Score</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="15%">Status</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Steps</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_refund_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7413</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_password_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.6900</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_cancel_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7413</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_delivery_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7300</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">3 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>easy_update_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7300</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">3 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_chargeback_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.4778</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">❌ FAIL</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_partial_refund_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.6913</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">6 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_tech_billing_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.4028</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">❌ FAIL</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_subscription_dispute_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.6800</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>med_api_quota_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7400</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_fraud_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7600</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_abuse_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.6258</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_enterprise_breach_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.8000</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_bulk_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.7200</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4 / 12</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>hard_gdpr_001</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0.8000</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅ PASS</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">5 / 12</td></tr>
</table>

---

## 🏆 The GRPO Success Story: Small Model, Large Impact

A 50× smaller model trained for 32 minutes on a T4 GPU to match the 72B Oracle.

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="32%">Model</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="18%">Training</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="16%">Easy Pass</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="16%">Medium Pass</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="16%">Hard Pass</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Overall</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Qwen-72B (Oracle baseline)</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">None</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">100%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">100%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">100%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>100%</b></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Qwen-1.5B (zero-shot)</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">None</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">40%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>13%</b></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>Qwen-1.5B (after GRPO)</b></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">32 min T4</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">100%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">80%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">40%</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><b>73%</b></td></tr>
</table>

![Reward Curve](omni-grpo-output/reward_curve.png)

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="22%">Phase</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="18%">Steps</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">What the Model Learned</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Exploration</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">0–40</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Basic JSON format compliance</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Improvement</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">40–85</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Correct tool ordering emerges</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Stable</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">85–125</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Fewer policy violations, correct escalation</td></tr>
</table>

### Four Reward Functions Used in GRPO Training

```python
reward_format(completion)        # Valid JSON with action_type + action_value → 0.0 / 0.3 / 1.0
reward_valid_action(completion)  # Known action_type → 0.0 or 0.5
reward_env(completion, task_id)  # Live environment reward → −0.30 to +0.15
reward_policy(completion)        # Policy compliance check → −0.30 / 0.0 / +0.10
```

---

## 🚀 Training Stack

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="25%">Component</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="18%">Version</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Role</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">OpenEnv</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">v0.2.3</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Standard reset() / step() interface</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">TRL GRPOTrainer</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">latest</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Rollout collection, reward aggregation, optimization</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Unsloth</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">latest</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">4-bit QLoRA, memory-efficient LoRA on T4</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Qwen2.5-1.5B-Instruct</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">—</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Training model — fits free Colab T4</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Qwen2.5-72B-Instruct</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">—</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Oracle baseline for evaluation</td></tr>
</table>

---

## Per-Task Episode Traces

<details>
<summary>Easy Tasks</summary>

![easy_refund_001](outputs/easy_refund_001.png)
![easy_password_001](outputs/easy_password_001.png)
![easy_cancel_001](outputs/easy_cancel_001.png)
![easy_delivery_001](outputs/easy_delivery_001.png)
![easy_update_001](outputs/easy_update_001.png)

</details>

<details>
<summary>Medium Tasks</summary>

![med_chargeback_001](outputs/med_chargeback_001.png)
![med_partial_refund_001](outputs/med_partial_refund_001.png)
![med_tech_billing_001](outputs/med_tech_billing_001.png)
![med_subscription_dispute_001](outputs/med_subscription_dispute_001.png)
![med_api_quota_001](outputs/med_api_quota_001.png)

</details>

<details>
<summary>Hard Tasks</summary>

![hard_fraud_001](outputs/hard_fraud_001.png)
![hard_abuse_001](outputs/hard_abuse_001.png)
![hard_enterprise_breach_001](outputs/hard_enterprise_breach_001.png)
![hard_bulk_001](outputs/hard_bulk_001.png)
![hard_gdpr_001](outputs/hard_gdpr_001.png)

</details>

---

## API Reference

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="22%">Endpoint</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="12%">Method</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Description</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>/health</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">GET</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Returns <code>{"status":"healthy"}</code></td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>/reset</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">POST</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Start new episode, returns SupportObservation</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>/step</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">POST</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Execute one action, returns obs + reward + done</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>/state</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">GET</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Current internal episode state</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>/docs</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">GET</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Swagger UI</td></tr>
</table>

```bash
curl -X POST https://shraddhashaha-omni-support-env.hf.space/reset \
  -H "Content-Type: application/json" -d '{"task_id": "hard_fraud_001"}'

curl -X POST https://shraddhashaha-omni-support-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"action_type": "check_account", "action_value": "USR_9901"}}'
```

---

## Quick Start

```bash
git clone https://github.com/shraddhashahaof/omni-support-env
cd omni-support-env
python -m venv venv && venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt

# Run all 15 tasks (local env, no HF Space needed)
python inference.py

# Run a single task
python inference.py hard_fraud_001

# Collect training data
python collect_training_data.py --episodes 300 --out data/rollouts.jsonl

# Simulated training (CPU, produces reward curve)
python train.py

# Real GPU training
python train.py --gpu
```

**PowerShell — run all 15 tasks with delay between each:**
```powershell
$tasks = @("easy_refund_001","easy_password_001","easy_cancel_001","easy_delivery_001",
           "easy_update_001","med_chargeback_001","med_partial_refund_001","med_tech_billing_001",
           "med_subscription_dispute_001","med_api_quota_001","hard_fraud_001","hard_abuse_001",
           "hard_enterprise_breach_001","hard_bulk_001","hard_gdpr_001")
foreach ($t in $tasks) { python inference.py $t; Start-Sleep -Seconds 5 }
```

---

## Docker

```bash
docker build -t omni-support-env:latest -f server/Dockerfile .
docker run -d --name omni-test -p 7860:7860 omni-support-env:latest
curl http://localhost:7860/health
```

---

## OpenEnv Compliance

<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left" width="70%">Requirement</th><th style="text-align:left;padding:8px;border:1px solid #d0d7de;background:#f6f8fa;word-wrap:break-word" align="left">Status</th></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Typed Action / Observation / State via Pydantic v2</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>reset()</code> returns SupportObservation</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>step(action)</code> returns observation + reward + done</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>state</code> property returns SupportState</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top"><code>openenv.yaml</code> with correct metadata + tags</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Deployed as Docker HF Space on port 7860</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Tagged <code>openenv</code> for Hub discovery</td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
<tr><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">Passes <code>openenv validate</code></td><td style="padding:8px;border:1px solid #d0d7de;word-wrap:break-word;vertical-align:top">✅</td></tr>
</table>

---

## Future Extensions

Multi-agent escalation teams (cooperative RL) · CRM integrations (Salesforce, Zendesk) · Long-term customer memory across episodes · Multilingual ticket support · RLHF layer with human feedback · Voice support workflows · Real-time analytics dashboard

---

**Built by Shraddha Shaha — Team AgentOne — Round 2, OpenEnv Hackathon India 2026**

[HF Space](https://huggingface.co/spaces/shraddhashaha/omni-support-env) · [GitHub](https://github.com/shraddhashahaof/omni-support-env) · [Live Demo](https://shraddhashaha-omni-support-env.hf.space)