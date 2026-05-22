import base64
import os
import logging
from logging.handlers import RotatingFileHandler
import uuid
import hashlib
import queue
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string, render_template
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from canary_web.models.forensics import Base, CanaryHit, ThreatLevel

class CyberCommandConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ultra_secure_deception_mesh_cipher_2026")
    DATABASE_URI = "sqlite:///canary_dev.db"
    DEBUG = True
    PORT = 5000
    HOST = "0.0.0.0"
    SYSTEM_BANNER = "Tactical-Deception-Mesh/v2.4.0-Enterprise"

app = Flask(__name__)
app.config.from_object(CyberCommandConfig)

# Endüstriyel Günlükleme
log_handler = RotatingFileHandler('canary_mesh_system.log', maxBytes=5000000, backupCount=10)
log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [SUBSYSTEM::%(name)s] %(message)s')
log_handler.setFormatter(log_formatter)

logger = logging.getLogger("TacticalCore")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

engine = create_engine(app.config["DATABASE_URI"], echo=False)
SessionLocal = sessionmaker(bind=engine)

# Asenkron Log Kuyruğu
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
        except Exception as e:
            db.rollback()
            logger.error(f"Kuyruk İşleme Hatası: {str(e)}")
        finally:
            db.close()
            log_queue.task_done()

worker_thread = threading.Thread(target=async_log_worker, daemon=True)
worker_thread.start()

# Tırnak işaretleri temizlenmiş güvenli kural üretici
def generate_tactical_firewall_rules(ip_address):
    return {
        "iptables": f"sudo iptables -A INPUT -s {ip_address} -j DROP -m comment --comment \"CANARY_DETECTION\"",
        "snort": f"drop tcp {ip_address} any -> $INTERNAL_NET any (msg:\"CANARY_DETECTION\"; sid:999001;)",
        "pfsense_api": f"curl -X POST https://pfsense.isu.edu/api/v1/block -d \"ip={ip_address}\""
    }

@app.after_request
def inject_enterprise_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net;"
    response.headers["Server"] = CyberCommandConfig.SYSTEM_BANNER
    return response

@app.context_processor
def inject_system_time():
    return {'now': datetime.now(timezone.utc)}

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
            
        return render_template(
            "dashboard.html", 
            hits=all_hits, total_hits=total_hits, 
            critical_hits=critical_hits, unique_tokens=unique_tokens
        )
    except Exception as e:
        return f"Database Integrity Anomaly: {str(e)}", 500
    finally:
        db.close()

@app.route("/api/v1/tokens/generate", methods=["POST"])
def generate_token():
    raw_uuid = str(uuid.uuid4())
    return jsonify({
        "status": "COMPLETED",
        "token_id": raw_uuid,
        "trigger_url": f"{request.url_root}t/{raw_uuid}"
    }), 201

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
                    window.location.href = "/error-page";
                }).catch(function() {
                    window.location.href = "/error-page";
                });
            };
        </script>
    </head>
    <body style="background-color: #020408;"></body>
    </html>
    """
    user_agent = request.headers.get("User-Agent", "").lower()
    if any(bot in user_agent for bot in ["curl", "wget", "python", "nikto", "nmap", "sqlmap"]):
        db = SessionLocal()
        try:
            hit = CanaryHit(
                token_id=uuid_id, ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"), referer=request.headers.get("Referer"),
                http_method=request.method, threat_level=ThreatLevel.HIGH,
                notes=f"CLI Taraması: {user_agent}"
            )
            hit.populate_datacenter_flag()
            if hit.is_vpn_or_tor: hit.threat_level = ThreatLevel.CRITICAL
            hit.set_fingerprint()
            db.add(hit)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
        return jsonify({"status": "Access Denied"}), 403

    return render_template_string(telemetry_js_template, token_id=uuid_id)

@app.route("/api/v1/telemetry/capture", methods=["POST"])
def telemetry_capture():
    data = request.get_json() or {}
    token_id = data.get("token_id")
    if not token_id: return jsonify({"status": "malformed"}), 400
    
    db = SessionLocal()
    try:
        hit = CanaryHit(
            token_id=token_id, ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"), referer=request.headers.get("Referer"),
            http_method="GET", screen_resolution=data.get("screen_resolution"),
            system_languages=data.get("system_languages"), threat_level=ThreatLevel.HIGH
        )
        hit.populate_datacenter_flag()
        if hit.is_vpn_or_tor: hit.threat_level = ThreatLevel.CRITICAL
        hit.set_fingerprint(extra=data.get("screen_resolution", ""))
        db.add(hit)
        db.commit()
        return jsonify({"status": "logged"}), 200
    except Exception:
        db.rollback()
        return jsonify({"status": "error"}), 500
    finally:
        db.close()

@app.route("/error-page")
def error_page():
    return "<h1>404 Not Found</h1>", 404

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(host=CyberCommandConfig.HOST, port=CyberCommandConfig.PORT, debug=CyberCommandConfig.DEBUG)
