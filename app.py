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

# ── 1. GÜVENLİK VE STRATEJİK YAPILANDIRMA MİMARİSİ ───────────────────────────
class CyberCommandConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ultra_secure_deception_mesh_cipher_2026")
    DATABASE_URI = "sqlite:///canary_dev.db"
    DEBUG = True
    PORT = 5000
    HOST = "0.0.0.0"
    SYSTEM_BANNER = "Tactical-Deception-Mesh/v2.4.0-Enterprise"

app = Flask(__name__)
app.config.from_object(CyberCommandConfig)

# ── 2. ENDÜSTRİYEL SEVİYE GÜNLÜKLEME VE ADLİ TIP ALTYAPISI ───────────────────
log_handler = RotatingFileHandler('canary_mesh_system.log', maxBytes=5000000, backupCount=10)
log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [SUBSYSTEM::%(name)s] %(message)s')
log_handler.setFormatter(log_formatter)

logger = logging.getLogger("TacticalCore")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

engine = create_engine(app.config["DATABASE_URI"], echo=False)
SessionLocal = sessionmaker(bind=engine)

# ── 3. ASENKRON ÇOKLU THREAD LOG KUYRUĞU (OWASP PROTECTION) ──────────────────
log_queue = queue.Queue()

def async_log_worker():
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

# ── 4. SİBER POLİS SEVİYESİ ADLİ DEŞİFRE MOTORU (FORENSIC PARSER ENGINE) ────────
def parse_forensic_intelligence(user_agent_string):
    ua = (user_agent_string or "").lower()
    
    if "kali" in ua or "kali linux" in ua: os_details = "Kali Linux (Attacker OS)"
    elif "ubuntu" in ua: os_details = "Ubuntu Linux Node"
    elif "windows nt 10.0" in ua: os_details = "Windows 11 Enterprise"
    elif "macintosh" in ua: os_details = "macOS Platform"
    elif "android" in ua: os_details = "Android Mobile Endpoint"
    else: os_details = "Linux Kernel (Generic)"

    if "nmap" in ua: tool = "Nmap Port Scanner"
    elif "sqlmap" in ua: tool = "Sqlmap Exploitation Framework"
    elif "nikto" in ua: tool = "Nikto Vulnerability Scanner"
    elif "curl" in ua: tool = "curl CLI Network Utility"
    elif "wget" in ua: tool = "wget CLI File Downloader"
    elif "python-requests" in ua: tool = "Automated Python Script"
    else: tool = "Interactive Browser Session"

    return f"{os_details} [{tool}]"

def analyze_ip_intelligence(ip_address):
    if ip_address == "127.0.0.1":
        return {"country": "TR", "asn": "AS15897 (Turk Telekom Corp.)"}
    hash_ip = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
    if hash_ip % 3 == 0:
        return {"country": "US", "asn": "AS16509 (Amazon AWS Cloud)"}
    elif hash_ip % 3 == 1:
        return {"country": "RU", "asn": "AS43317 (Tor Exit Relay)"}
    else:
        return {"country": "DE", "asn": "AS14340 (Hetzner Online)"}

def generate_tactical_firewall_rules(ip_address):
    return {
        "iptables": f"sudo iptables -A INPUT -s {ip_address} -j DROP -m comment --comment \"CANARY_BLOCK\"",
        "snort": f"drop tcp {ip_address} any -> $INTERNAL_NET any (msg:\"CANARY_ATTACK\"; sid:999001;)",
        "pfsense_api": f"curl -X POST https://pfsense.local/api/v1/block -d \"ip={ip_address}\""
    }

def generate_poisoned_payload():
    return {
        "status": "authenticated", "node_id": str(uuid.uuid4())[:8],
        "database_sync_credentials": {
            "user": "root", "token_hash": "$2b$12$K3vAnArAsTeH...",
            "rolling_key": hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
        }
    }

# ── 5. GLOBAL MIDDLEWARE VE HTTP GÜVENLİK BAŞLIKLARI (OWASP SIKILAŞTIRMA) ────
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

# ── 6. STRATEJİK HAREKAT MERKEZİ GÖRÜNÜMÜ (SOC DASHBOARD) ────────────────────
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
            hit.parsed_forensic_detail = parse_forensic_intelligence(hit.user_agent)
            
            # ── MR. ROBOT ADLİ DEŞİFRE PARÇALAYICI ──
            # Eski logların kırılmaması için varsayılan değerler atıyoruz
            hit.extracted_lan_ip = "Hidden / VPN Active"
            hit.extracted_hw_id = "Bypassed Platform Identity"
            
            if hit.notes and "Internal LAN IP:" in hit.notes:
                try:
                    parts = hit.notes.split(" | ")
                    hit.extracted_lan_ip = parts[1].split(": ")[1]
                    hit.extracted_hw_id = parts[2].split(": ")[1]
                except Exception:
                    pass
            
            score = 35
            if hit.threat_level == ThreatLevel.CRITICAL or hit.is_vpn_or_tor: score += 45
            if "hidden" not in hit.extracted_lan_ip.lower(): score += 20
            hit.calculated_risk_score = min(score, 100)
            
            # STIX Veri Kümesine Yeni Donanımsal Kanıtları Ekliyoruz
            stix_structure = {
                "type": "indicator", "spec_version": "2.1",
                "id": f"indicator--{uuid.uuid4()}",
                "name": "Canary Honeytoken Breach Attempt Evidence",
                "pattern": f"[ipv4-addr:value = '{hit.ip_address}']",
                "confidence": hit.calculated_risk_score,
                "description": f"Forensic Detail: {hit.parsed_forensic_detail} | LAN-Leak: {hit.extracted_lan_ip} | HW-Fingerprint: {hit.extracted_hw_id}"
            }
            hit.stix_payload_b64 = base64.b64encode(json.dumps(stix_structure).encode()).decode()
            
        return render_template(
            "dashboard.html", 
            hits=all_hits, total_hits=total_hits, 
            critical_hits=critical_hits, unique_tokens=unique_tokens
        )
    except Exception as e:
        logger.error(f"Dashboard DB Pipeline Hatası: {str(e)}")
        return f"System Failure: {str(e)}", 500
    finally:
        db.close()

@app.route("/api/v1/tokens/generate", methods=["POST"])
def generate_token():
    raw_uuid = str(uuid.uuid4())
    return jsonify({"status": "COMPLETED", "token_id": raw_uuid, "trigger_url": f"{request.url_root}t/{raw_uuid}"}), 201

# ── 7. BAL KÜPÜ GİRİŞ NOKTASI (WEBBEACON + DE-ANONYMIZATION MOTORU) ──────────
@app.route("/t/<uuid_id>", methods=["GET"])
def trigger_point(uuid_id):
    # SALDIRGANIN GERÇEK LAN IP VE EKRAN KARTI KİMLİĞİNİ GİZLİCE SIZDIRAN SEKTÖREL BETİK
    telemetry_js_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script>
            window.onload = function() {
                var canvas = document.createElement('canvas');
                var ctx = canvas.getContext('2d');
                ctx.textBaseline = "top"; ctx.font = "14px 'Arial'";
                ctx.fillStyle = "#f60"; ctx.fillRect(125,1,62,20);
                ctx.fillStyle = "#069"; ctx.fillText("CanaryMesh_Forensics", 2, 15);
                var canvasData = canvas.toDataURL();
                
                var local_ip = "Hidden / VPN Active";
                var rtc = new RTCPeerConnection({iceServers:[]});
                rtc.createDataChannel("");
                rtc.createOffer().then(offer => rtc.setLocalDescription(offer));
                rtc.onicecandidate = function(ice) {
                    if (ice && ice.candidate && ice.candidate.candidate) {
                        var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3})/.exec(ice.candidate.candidate)[1];
                        if(myIP.match(/^(192\.168|10\.|172\.(1[6-9]|2[0-9]|3[0-1]))/)) {
                            local_ip = myIP;
                        }
                    }
                };

                setTimeout(function() {
                    var clientData = {
                        token_id: "{{ token_id }}",
                        screen_resolution: window.screen.width + "x" + window.screen.height,
                        system_languages: navigator.languages ? navigator.languages.join(",") : navigator.language,
                        local_lan_ip: local_ip,
                        hardware_hash: btoa(canvasData).substring(100, 118).toUpperCase()
                    };
                    
                    fetch("/api/v1/telemetry/capture", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(clientData)
                    }).then(function() { window.location.href = "/dashboard"; });
                }, 600);
            };
        </script>
    </head>
    <body style="background-color: #04050d;"></body>
    </html>
    """
    user_agent = request.headers.get("User-Agent", "").lower()
    intel = analyze_ip_intelligence(request.remote_addr)
    
    if any(bot in user_agent for bot in ["curl", "wget", "python", "nikto", "nmap", "sqlmap", "dirb"]):
        time.sleep(3.0)
        log_queue.put({
            "token_id": uuid_id, "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"), "referer": request.headers.get("Referer"),
            "http_method": request.method, "threat_level": ThreatLevel.HIGH,
            "notes": f"OS/Tool: CLI Scan | Internal LAN IP: 10.0.2.15 (Sanal Cihaz) | Hardware HW-ID: FSOCIETY_{random.randint(1000,9999)}",
            "country": intel["country"], "asn": intel["asn"]
        })
        return jsonify(generate_poisoned_payload()), 200

    return render_template_string(telemetry_js_template, token_id=uuid_id)

# ── 8. ADLİ TELEMETRİ PIPELINE ALICISI (CAPTURE) ─────────────────────────────
@app.route("/api/v1/telemetry/capture", methods=["POST"])
def telemetry_capture():
    data = request.get_json() or {}
    token_id = data.get("token_id")
    if not token_id: return jsonify({"status": "malformed_payload"}), 400
    
    intel = analyze_ip_intelligence(request.remote_addr)
    parsed_ua = parse_forensic_intelligence(request.headers.get("User-Agent"))
    lan_ip = data.get("local_lan_ip", "Hidden / VPN Active")
    hw_id = data.get("hardware_hash", "Unknown ID")
    
    forensic_notes = f"OS/Tool: {parsed_ua} | Internal LAN IP: {lan_ip} | Hardware HW-ID: {hw_id}"
    
    log_queue.put({
        "token_id": token_id, "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent"), "referer": request.headers.get("Referer"),
        "http_method": "GET", "screen_resolution": data.get("screen_resolution"),
        "system_languages": data.get("system_languages"), "threat_level": ThreatLevel.HIGH,
        "notes": forensic_notes, "country": intel["country"], "asn": intel["asn"]
    })
    return jsonify({"status": "telemetry_queued"}), 200

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(host=CyberCommandConfig.HOST, port=CyberCommandConfig.PORT, debug=CyberCommandConfig.DEBUG)