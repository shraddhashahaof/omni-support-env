# server/app.py
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openenv.core.env_server import create_fastapi_app
from environment import OmniSupportEnvironment
from models import SupportAction, SupportObservation

# ── Build the OpenEnv app ─────────────────────────────────────────────────────
app = create_fastapi_app(OmniSupportEnvironment, SupportAction, SupportObservation)

# ── Track basic live stats ────────────────────────────────────────────────────
_stats = {"episodes": 0, "steps": 0, "started": time.time()}

_orig_reset = OmniSupportEnvironment.reset
_orig_step  = OmniSupportEnvironment.step

def _patched_reset(self, *a, **kw):
    _stats["episodes"] += 1
    return _orig_reset(self, *a, **kw)

def _patched_step(self, *a, **kw):
    _stats["steps"] += 1
    return _orig_step(self, *a, **kw)

OmniSupportEnvironment.reset = _patched_reset
OmniSupportEnvironment.step  = _patched_step

# ── Dashboard HTML ────────────────────────────────────────────────────────────
DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="15">
<title>OmniSupportEnv v2</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,sans-serif;background:#0f1117;color:#e0e0e0;padding:2rem}
  h1{font-size:1.6rem;color:#fff;margin-bottom:.25rem}
  .sub{color:#888;font-size:.9rem;margin-bottom:2rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1rem;margin-bottom:2rem}
  .card{background:#1a1d27;border:1px solid #2a2d3a;border-radius:10px;padding:1.25rem}
  .card h3{font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem}
  .card .val{font-size:2rem;font-weight:700;color:#7c6af7}
  .card .note{font-size:.78rem;color:#666;margin-top:.3rem}
  .section{background:#1a1d27;border:1px solid #2a2d3a;border-radius:10px;padding:1.5rem;margin-bottom:1.5rem}
  .section h2{font-size:1rem;color:#aaa;margin-bottom:1rem;border-bottom:1px solid #2a2d3a;padding-bottom:.5rem}
  table{width:100%;border-collapse:collapse;font-size:.85rem}
  th{text-align:left;color:#888;padding:.4rem .6rem;border-bottom:1px solid #2a2d3a}
  td{padding:.5rem .6rem;border-bottom:1px solid #1e2130}
  .badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.75rem;font-weight:600}
  .easy{background:#1a3a1a;color:#4caf50}.medium{background:#3a2e00;color:#ffc107}.hard{background:#3a1a1a;color:#f44336}
  .ep{background:#1e2130;border-radius:6px;padding:.75rem 1rem;margin:.4rem 0;font-family:monospace;font-size:.85rem}
  .method{color:#7c6af7;font-weight:700;margin-right:.5rem}.path{color:#64b5f6}
  .desc{color:#888;font-size:.8rem;margin-top:.2rem}
  code{background:#0f1117;padding:2px 6px;border-radius:3px;font-size:.8rem;color:#80cbc4}
  pre{background:#0f1117;padding:1rem;border-radius:6px;font-size:.82rem;overflow-x:auto;color:#80cbc4}
  a{color:#7c6af7;text-decoration:none}a:hover{text-decoration:underline}
  .green{color:#4caf50}
  .note{color:#555;font-size:.75rem;text-align:right;margin-top:1rem}
</style>
</head>
<body>
<h1>🤖 OmniSupportEnv</h1>
<p class="sub">Multi-Step Customer Operations RL Environment &nbsp;·&nbsp;
  <a href="/docs" target="_blank">API Docs ↗</a>
</p>

<div class="grid">
  <div class="card"><h3>Episodes run</h3><div class="val">{episodes}</div><div class="note">since deploy</div></div>
  <div class="card"><h3>Steps processed</h3><div class="val">{steps}</div><div class="note">total agent actions</div></div>
  <div class="card"><h3>Tasks available</h3><div class="val">15</div><div class="note">5 easy · 5 med · 5 hard</div></div>
  <div class="card"><h3>Uptime</h3><div class="val" style="font-size:1.3rem">{uptime}</div><div class="green">● healthy</div></div>
</div>

<div class="section">
  <h2>API Endpoints</h2>
  <div class="ep"><span class="method">POST</span><span class="path">/reset</span>
    <div class="desc">Start episode. Body: <code>{{"task_id": "easy_refund_001"}}</code> — omit for random task</div></div>
  <div class="ep"><span class="method">POST</span><span class="path">/step</span>
    <div class="desc">Take action. Body: <code>{{"action": {{"action_type": "check_account", "action_value": "USR_4821"}}}}</code></div></div>
  <div class="ep"><span class="method">GET</span><span class="path">/health</span>
    <div class="desc">Health check</div></div>
</div>

<div class="section">
  <h2>Task Library</h2>
  <table>
    <tr><th>ID</th><th>Difficulty</th><th>Scenario</th><th>Required tools</th></tr>
    <tr><td>easy_refund_001</td><td><span class="badge easy">EASY</span></td><td>Duplicate charge</td><td>lookup_order, process_refund</td></tr>
    <tr><td>easy_password_001</td><td><span class="badge easy">EASY</span></td><td>Password reset</td><td>check_account, search_kb</td></tr>
    <tr><td>easy_cancel_001</td><td><span class="badge easy">EASY</span></td><td>Cancel subscription</td><td>check_account</td></tr>
    <tr><td>easy_delivery_001</td><td><span class="badge easy">EASY</span></td><td>Late delivery</td><td>lookup_order</td></tr>
    <tr><td>easy_update_001</td><td><span class="badge easy">EASY</span></td><td>Billing address</td><td>search_kb</td></tr>
    <tr><td>med_chargeback_001</td><td><span class="badge medium">MEDIUM</span></td><td>Chargeback threat</td><td>lookup_order, check_account, process_refund</td></tr>
    <tr><td>med_partial_refund_001</td><td><span class="badge medium">MEDIUM</span></td><td>Damaged product</td><td>lookup_order, check_account, search_kb</td></tr>
    <tr><td>med_tech_billing_001</td><td><span class="badge medium">MEDIUM</span></td><td>App crash + billing</td><td>search_kb, check_account, process_refund</td></tr>
    <tr><td>med_subscription_dispute_001</td><td><span class="badge medium">MEDIUM</span></td><td>Subscription dispute</td><td>check_account, lookup_order, process_refund</td></tr>
    <tr><td>med_api_quota_001</td><td><span class="badge medium">MEDIUM</span></td><td>Enterprise quota</td><td>check_account, search_kb, escalate</td></tr>
    <tr><td>hard_fraud_001</td><td><span class="badge hard">HARD</span></td><td>Fraud — new account</td><td>check_account, flag_security, escalate</td></tr>
    <tr><td>hard_abuse_001</td><td><span class="badge hard">HARD</span></td><td>Serial refund abuser</td><td>check_account, lookup_order, search_kb</td></tr>
    <tr><td>hard_enterprise_breach_001</td><td><span class="badge hard">HARD</span></td><td>API key compromised</td><td>check_account, flag_security, search_kb, escalate</td></tr>
    <tr><td>hard_bulk_001</td><td><span class="badge hard">HARD</span></td><td>Reseller bulk demand</td><td>check_account, search_kb, escalate</td></tr>
    <tr><td>hard_gdpr_001</td><td><span class="badge hard">HARD</span></td><td>GDPR + hack + refund</td><td>check_account, flag_security, search_kb, escalate</td></tr>
  </table>
</div>

<div class="section">
  <h2>Quick Start</h2>
  <pre>
# 1. Start an episode
curl -X POST {space_url}/reset -H "Content-Type: application/json" -d '{{"task_id": "easy_refund_001"}}'

# 2. Take a step
curl -X POST {space_url}/step -H "Content-Type: application/json" \\
     -d '{{"action": {{"action_type": "check_account", "action_value": "USR_4821"}}}}'

# 3. Run the full agent
python inference.py          # all 15 tasks
python inference.py easy_refund_001 hard_fraud_001   # specific tasks</pre>
</div>

<div class="section">
  <h2>Scoring Breakdown</h2>
  <table>
    <tr><th>Component</th><th>Weight</th><th>What it measures</th></tr>
    <tr><td>Resolution</td><td>40%</td><td>Correct ticket resolution type + keywords</td></tr>
    <tr><td>Tool use</td><td>25%</td><td>Right tools used, minimal extras</td></tr>
    <tr><td>Policy compliance</td><td>20%</td><td>No policy violations</td></tr>
    <tr><td>Efficiency</td><td>15%</td><td>Steps taken vs expected</td></tr>
  </table>
</div>

<p class="note">Auto-refreshes every 15s</p>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    secs = int(time.time() - _stats["started"])
    h, r = divmod(secs, 3600); m, s = divmod(r, 60)
    uptime = f"{h}h {m}m" if h else f"{m}m {s}s"
    return HTMLResponse(DASHBOARD.format(
        episodes=_stats["episodes"], steps=_stats["steps"],
        uptime=uptime,
        space_url="https://shraddhashaha-omni-support-env.hf.space",
    ))


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")

if __name__ == "__main__":
    main()