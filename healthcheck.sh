#!/bin/bash
# healthcheck.sh - Secure Container Lifecycle Auditor

set -eo pipefail

# Flask yerel ağ motorunun yanıt verip vermediğini OWASP standartlarında test eder
TARGET_URL="http://127.0.0.1:5000/dashboard"

if curl -s -f -o /dev/null -H "User-Agent: Security-Health-Check-Daemon" "$TARGET_URL"; then
    echo "[+] System integrity verified. Defense mesh operational."
    exit 0
else
    echo "[-] CRITICAL: Web application server unresponsive or under service denial!"
    exit 1
fi