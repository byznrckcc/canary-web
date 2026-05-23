import base64
import os
import logging
from logging.handlers import RotatingFileHandler
import uuid
import hashlib
import queue
import threading
import time
import json
import random
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string, render_template
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from canary_web.models.forensics import Base, CanaryHit, ThreatLevel

# ── 1. KURUMSAL GÜVENLİK VE STRATEJİK YAPILANDIRMA MİMARİSİ ──────────────────
class CyberCommandConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ultra_secure_deception_mesh_cipher_2026")
    DATABASE_URI = "sqlite:///canary_dev.db"
    DEBUG = True
    PORT = 5000
    HOST = "0.0.0.0"
    SYSTEM_BANNER = "Tactical-Deception-Mesh/v2.4.0-Enterprise"

app = Flask(__name__)
app.config.from_object(CyberCommandConfig)

# ── 2. ENDÜSTRİYEL SEVİYE GÜNLÜKLEME VE ADLİ TIP KAYIT ALTYAPISI ─────────────
log_handler = RotatingFileHandler('canary_mesh_system.log', maxBytes=5000000, backupCount=10)
log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [SUBSYSTEM::%(name)s] %(message)s')
log_handler.setFormatter(log_formatter)

logger = logging.getLogger("TacticalCore")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

engine = create_engine(app.config["DATABASE_URI"], echo=False)
SessionLocal = sessionmaker(bind=engine)

# ── 3. ASENKRON ÇOKLU THREAD LOG KUYRUĞU (HIGH-PERFORMANCE FORENSIC QUEUE) ───
log_queue = queue.Queue()

def async_log_worker():
    """Arka planda sessizce çalışan, ana thread'i yormadan logları DB'ye işleyen motor."""
    while True:
        hit_data = log_queue.get()
        if hit_data is None:
            break
        db = SessionLocal()
        try:
            hit = CanaryHit(
                token_id=hit_data['token_id'], ip_address=hit_data['ip_address'],
                user_agent=hit_data['user_agent'], referer=hit_data['referer'],
                http_method=hit_data['http_method'], screen_resolution=hit_data.get('screen_resolution'),
                system_languages=hit_data.get('system_languages'), threat_level=hit_data['threat_level'],
                notes=hit_data.get('notes'), country=hit_data.get('country'), asn=hit_data.get('asn')
            )
            hit.populate_datacenter_flag()
            if hit.is_vpn_or_tor:
                hit.threat_level = ThreatLevel.CRITICAL
            hit.set_fingerprint(extra=hit_data.get('screen_resolution', ''))
            db.add(hit)
            db.commit()
            logger.info(f"[+] Asenkron Log Başarıyla İşlendi. IP: {hit.ip_address}")
        except Exception as e:
            db.rollback()
            logger.error(f"[-] Adli Kayıt İşleme Hatası: {str(e)}")
        finally:
            db.close()
            log_queue.task_done()

worker_thread = threading.Thread(target=async_log_worker, daemon=True)
worker_thread.start()

# ── 4. SİBER TEHDİT İSTİHBARATI VE COĞRAFİ SİMÜLATÖR ─────────────────────────
def analyze_ip_intelligence(ip_address):
    """Gelen IP adresini lokal siber istihbarat havuzundan geçirerek analiz eder."""
    if ip_address == "127.0.0.1":
        return {"country": "TR", "asn": "AS15897 (Turk Telekom)", "is_datacenter": False}
    
    hash_ip = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
    if hash_ip % 3 == 0:
        return {"country": "US", "asn": "AS16509 (Amazon.com Cloud Node)", "is_datacenter": True}
    elif hash_ip % 3 == 1:
        return {"country": "NL", "asn": "AS43317 (Tor Exit Relay Node)", "is_datacenter": True}
    else:
        return {"country": "DE", "asn": "AS14340 (Hetzner Online GmbH)", "is_datacenter": True}

def generate_tactical_firewall_rules(ip_address):
    """Saldırgan tespit edildiği an üretilen dinamik güvenlik duvarı savunma komutları."""
    return {
        "iptables": f"sudo iptables -A INPUT -s {ip_address} -j DROP -m comment --comment \"CANARY_WEB_BLOCK\"",
        "snort": f"drop tcp {ip_address} any -> $INTERNAL_NET any (msg:\"CANARY_ATTACK\"; sid:999001;)",
        "pfsense_api": f"curl -X POST https://pfsense.local/api/v1/block -d \"ip={ip_address}\""
    }

# ── 5. KRİPTOGRAFİK VERİ ZEHİRLEME MOTORU (DECOY PAYLOAD POISONING) ──────────
def generate_poisoned_payload():
    """Hacker'ı oyalamak ve gerçek bir sızıntı olduğuna inandırmak için sahte kritik veri üretir."""
    fake_users = ["root", "admin", "db_sync", "infra_core", "backup_agent"]
    fake_hashes = ["$2b$12$K3vAnArAsTeH...", "$2b$12$IsTiNyEUnIv...", "$2b$12$B1l1s1mGuV..."]
    
    decoy_data = {
        "status": "authenticated",
        "mesh_node_id": str(uuid.uuid4())[:8],
        "database_sync_credentials": {
            "user": random.choice(fake_users),
            "token_hash": random.choice(fake_hashes),
            "rolling_key": hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
        },
        "internal_routing_vault": [
            {"vault_id": "VAULT-AWS-01", "access_key": f"AKIAIOSFODNN7_{random.randint(1000,9999)}"},
            {"vault_id": "VAULT-PROD-DB", "connection_string": "postgresql://db_master:P@ssw0rd2026@10.0.4.15:5432/main"}
        ]
    }
    return decoy_data

# ── 6. GLOBAL MIDDLEWARE VE HTTP GÜVENLİK BAŞLIKLARI (OWASP HARDENING) ───────
@app.after_request
def inject_enterprise_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
    response.headers["Server"] = CyberCommandConfig.SYSTEM_BANNER
    return response

@app.context_processor
def inject_system_time():
    return {'now': datetime.now(timezone.utc)}

# ── 7. PLATFORM ROTASI: STRATEJİK HAREKAT MERKEZİ (SOC DASHBOARD) ───────────
@app.route("/dashboard", methods=["GET"])
def dashboard_view():
    db = SessionLocal()
    try:
        all_hits = db.query(CanaryHit).order_by(CanaryHit.created_at.desc()).all()
        total_hits = len(all_hits)
        critical_hits = db.query(CanaryHit).filter(CanaryHit.threat_level == ThreatLevel.CRITICAL).count()
        unique_tokens = db.query(func.count(CanaryHit.token_id.distinct())).scalar() or 0
        
        for hit in all_hits:
            hit.generated_rules = generate_tactical_firewall_rules(hit.ip_address or "127.0.0.1")
            
            # Algoritmik Tehdit Skoru Hesaplama
            score = 35
            if hit.threat_level == ThreatLevel.CRITICAL or hit.is_vpn_or_tor: 
                score += 45
            if not hit.screen_resolution: 
                score += 20  
            hit.calculated_risk_score = min(score, 100)
            
            # Uluslararası Standartta Tehdit İstihbarat Çıktısı (STIX CTI Standard)
            stix_structure = {
                "type": "indicator", "spec_version": "2.1",
                "id": f"indicator--{uuid.uuid4()}",
                "name": "Canary Honeytoken Breach Attempt Evidence",
                "pattern": f"[ipv4-addr:value = '{hit.ip_address}']",
                "confidence": hit.calculated_risk_score,
                "description": f"Forensic Artifact: {hit.notes or 'Captured via tactical defense mesh.'}"
            }
            hit.stix_payload_b64 = base64.b64encode(json.dumps(stix_structure).encode()).decode()
            
        return render_template(
            "dashboard.html", 
            hits=all_hits, total_hits=total_hits, 
            critical_hits=critical_hits, unique_tokens=unique_tokens
        )
    except Exception as e:
        logger.error(f"Dashboard DB Pipeline Hatası: {str(e)}")
        return f"System Matrix Failure: {str(e)}", 500
    finally:
        db.close()

# ── 8. PLATFORM ROTASI: SENSÖR GENERATOR API ─────────────────────────────────
@app.route("/api/v1/tokens/generate", methods=["POST"])
def generate_token():
    raw_uuid = str(uuid.uuid4())
    return jsonify({
        "status": "COMPLETED",
        "token_id": raw_uuid,
        "trigger_url": f"{request.url_root}t/{raw_uuid}"
    }), 201

# ── 9. GÜVENLİK ROTASI: BAL KÜPÜ GİRİŞ NOKTASI (WEB BEACON & ACTIVE TARPIT) ──
@app.route("/t/<uuid_id>", methods=["GET"])
def trigger_point(uuid_id):
    telemetry_js_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script>
            window.onload = function() {
                var clientData = {
                    token_id: "{{ token_id }}",
                    screen_resolution: window.screen.width + "x" + window.screen.height,
                    system_languages: navigator.languages ? navigator.languages.join(",") : navigator.language
                };
                fetch("/api/v1/telemetry/capture", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(clientData)
                }).then(function() {
                    window.location.href = "/dashboard";
                }).catch(function() {
                    window.location.href = "/dashboard";
                });
            };
        </script>
    </head>
    <body style="background-color: #04050d;"></body>
    </html>
    """
    user_agent = request.headers.get("User-Agent", "").lower()
    intel = analyze_ip_intelligence(request.remote_addr)
    
    # Active Tarpit (Oyalama Tuzağı) Tetikleyici Mekanizması
    if any(bot in user_agent for bot in ["curl", "wget", "python", "nikto", "nmap", "sqlmap", "dirb"]):
        time.sleep(3.0)
        log_queue.put({
            "token_id": uuid_id, "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"), "referer": request.headers.get("Referer"),
            "http_method": request.method, "threat_level": ThreatLevel.HIGH,
            "notes": "Active Tarpit Enforced: Automated scanning tool delayed and poisoned.",
            "country": intel["country"], "asn": intel["asn"]
        })
        return jsonify(generate_poisoned_payload()), 200

    return render_template_string(telemetry_js_template, token_id=uuid_id)

# ── 10. ADLİ TELEMETRİ PIPELINE ALICISI (CAPTURE) ────────────────────────────
@app.route("/api/v1/telemetry/capture", methods=["POST"])
def telemetry_capture():
    data = request.get_json() or {}
    token_id = data.get("token_id")
    if not token_id: 
        return jsonify({"status": "malformed_payload"}), 400
    
    intel = analyze_ip_intelligence(request.remote_addr)
    
    log_queue.put({
        "token_id": token_id, "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent"), "referer": request.headers.get("Referer"),
        "http_method": "GET", "screen_resolution": data.get("screen_resolution"),
        "system_languages": data.get("system_languages"), "threat_level": ThreatLevel.HIGH,
        "notes": "Deep browser forensics payload analyzed and stored asynchronously.",
        "country": intel["country"], "asn": intel["asn"]
    })
    return jsonify({"status": "telemetry_queued"}), 200

# ── 11. KUSURSUZ MAİN TETİKLEYİCİ KATMANI ────────────────────────────────────
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("[+] 🔒 SİBER KOMUTA MERKEZİ: GELİŞMİŞ ALDATMACA MOTORU AKTİF!")
    app.run(host=CyberCommandConfig.HOST, port=CyberCommandConfig.PORT, debug=CyberCommandConfig.DEBUG)