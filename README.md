---
title: OmniSupportEnv
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# OmniSupportEnv

Multi-step customer operations simulator for RL agent training and evaluation.

## What it simulates
An AI agent handles enterprise support tickets — billing disputes, fraud detection,
technical issues, GDPR requests — using tools and company policy enforcement.

## Action space
| action_type     | action_value example                     |
|-----------------|------------------------------------------|
| search_kb       | "refund policy"                          |
| lookup_order    | "78234"                                  |
| check_account   | "USR_4821"                               |
| process_refund  | "78234, 49.99, duplicate charge"         |
| flag_security   | "USR_9901, suspected fraud"              |
| ask_user        | "Can you confirm your order number?"     |
| send_response   | "Your refund has been processed."        |
| escalate        | "Chargeback requires billing specialist" |
| resolve         | "Issue resolved, ticket closed"          |
| close_no_action | "Spam ticket"                            |

## Observation space
ticket_text, user_id, account_tier, account_age_days,
conversation_history, tool_results, policy_violations,
step_number, steps_remaining, last_feedback, cumulative_reward

## Tasks
| ID                         | Difficulty | Scenario                          |
|---------------------------|------------|-----------------------------------|
| easy_refund_001            | easy       | Duplicate charge refund           |
| easy_password_001          | easy       | Account locked                    |
| easy_cancel_001            | easy       | Subscription cancellation         |
| easy_delivery_001          | easy       | Missing delivery                  |
| easy_update_001            | easy       | Billing address update            |
| med_chargeback_001         | medium     | Chargeback + delivery dispute     |
| med_partial_refund_001     | medium     | Damaged goods partial refund      |
| med_tech_billing_001       | medium     | App crash + billing credit        |
| med_subscription_dispute_001 | medium   | Cancelled but still charged       |
| med_api_quota_001          | medium     | Enterprise quota exceeded         |
| hard_fraud_001             | hard       | Fraud detection trap              |
| hard_abuse_001             | hard       | Serial refund abuser              |
| hard_enterprise_breach_001 | hard      | API key compromised               |
| hard_bulk_001              | hard       | Bulk reseller demands             |
| hard_gdpr_001              | hard       | GDPR + hack + refund combined     |

## Reward design
- **Step reward** (dense): fires every action — +0.08 for using required tools,
  +0.12 for correct security flag, -0.20 for falling into fraud trap
- **Episode reward** (final): weighted sum — resolution(40%) + tool_use(25%) +
  policy(20%) + efficiency(15%)

## Baseline scores (Qwen2.5-72B-Instruct)
| Task       | Score |
|------------|-------|
| easy       | ~0.65 |
| medium     | ~0.45 |
| hard       | ~0.25 |

## Setup
```bash
pip install openenv-core
docker pull YOUR_HF_USERNAME-omni-support-env.hf.space
python inference.py
```

## Environment variables
```
HF_TOKEN=hf_...
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
```