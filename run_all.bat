@echo off
echo Running all 15 tasks with 15s gap...

python inference.py easy_refund_001
timeout 15 > nul

python inference.py easy_password_001
timeout 15 > nul

python inference.py easy_cancel_001
timeout 15 > nul

python inference.py easy_delivery_001
timeout 15 > nul

python inference.py easy_update_001
timeout 15 > nul

python inference.py med_chargeback_001
timeout 15 > nul

python inference.py med_partial_refund_001
timeout 15 > nul

python inference.py med_tech_billing_001
timeout 15 > nul

python inference.py med_subscription_dispute_001
timeout 15 > nul

python inference.py med_api_quota_001
timeout 15 > nul

python inference.py hard_fraud_001
timeout 15 > nul

python inference.py hard_abuse_001
timeout 15 > nul

python inference.py hard_enterprise_breach_001
timeout 15 > nul

python inference.py hard_bulk_001
timeout 15 > nul

python inference.py hard_gdpr_001

echo.
echo All 15 tasks done!
pause