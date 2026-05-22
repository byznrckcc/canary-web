import base64
import os
import logging
from logging.handlers import RotatingFileHandler
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string, render_template
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from canary_web.models.forensics import Base, CanaryHit, ThreatLevel

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cyber_command_ultra_secret_2026")
    DATABASE_URI = "sqlite:///canary_dev.db"
    DEBUG = True
    PORT = 5000
    HOST = "0.0.0.0"

app = Flask(__name__)
app.config.from_object(Config)

# Endüstriyel Günlükleme
log_handler = RotatingFileHandler('canary_system.log', maxBytes=2000000, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(subsystem)s] %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger("CanaryTactical")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

engine = create_engine(app.config["DATABASE_URI"], echo=False)
SessionLocal = sessionmaker(bind=engine)

# ── AKTİF DUVAR KURALI ÜRETİCİSİ (FIREWALL RULE GENERATOR ENGINE) ──────────
def generate_firewall_rules(ip_address):
    """Saldırgan yakalandığı an jüriye gösterilecek canlı engelleme betikleri."""
    return {
        "iptables": f"sudo iptables -A INPUT -s {ip_address} -j DROP -m comment --comment 'CANARY-WEB EXPLOIT TRAP'",
        "snort": f"drop tcp {ip_address} any -> $WM_NET any (msg:'CANARY-WEB INTENTIONAL TRAP HIT'; sid:9900001; rev:1;)",
        "pfsense_api": f"curl -X POST https://pfsense.local/api/v1/firewall/block -d 'ip={ip_address}&reason=canary_hit'"
    }

# ── GLOBAL MİDDLEWARE VE HATA YAKALAYICILAR ─────────────────────────────────
@app.after_request
def inject_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net;"
    response.headers["Server"] = "Tactical-Defense-Mesh"
    return response

@app.app_context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

# ── ROUTE 1: SİBER KOMUTA MERKEZİ (DASHBOARD) ───────────────────────────────
@app.route("/dashboard", methods=["GET"])
def dashboard_view():
    db = SessionLocal()
    try:
        all_hits = db.query(CanaryHit).order_by(CanaryHit.created_at.desc()).all()
        total_hits = len(all_hits)
        critical_hits = db.query(CanaryHit).filter(CanaryHit.threat_level == ThreatLevel.CRITICAL).count()
        unique_tokens = db.query(func.count(CanaryHit.token_id.distinct())).scalar() or 0
        
        # Her log girişi için dinamik firewall kurallarını oluşturup nesneye enjekte ediyoruz
        for hit in all_hits:
            hit.generated_rules = generate_firewall_rules(hit.ip_address or "127.0.0.1")
            
        return render_template(
            "dashboard.html", 
            hits=all_hits, total_hits=total_hits, 
            critical_hits=critical_hits, unique_tokens=unique_tokens
        )
    except Exception as e:
        return f"Database Integrity Anomaly: {str(e)}", 500
    finally:
        db.close()

# ── ROUTE 2: BAL KÜPÜ LİNK ÜRETİCİ (API) ────────────────────────────────────
@app.route("/api/v1/tokens/generate", methods=["POST"])
def generate_token():
    generated_uuid = str(uuid.uuid4())
    return jsonify({
        "status": "Aktivasyon Başarılı",
        "token_id": generated_uuid,
        "deception_matrix": {
            "web_beacon_url": f"{request.url_root}t/{generated_uuid}",
            "wordpress_trap_url": f"{request.url_root}wp-admin/auth/{generated_uuid}",
            "cloud_vault_url": f"{request.url_root}api/v2/vault/credentials/{generated_uuid}"
        }
    }), 201

# ── ROUTE 3: GENİŞLETİLMİŞ MODÜL - WORDPRESS GİRİŞ TUZAĞI (`/wp-admin`) ────
@app.route("/wp-admin/auth/<uuid_id>", methods=["GET", "POST"])
def wordpress_trap(uuid_id):
    """Saldırganların en çok taradığı dizin olan wp-admin için özel aldatmaca rotası."""
    db = SessionLocal()
    try:
        hit = CanaryHit(
            token_id=f"wp_trap_{uuid_id[:8]}", ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"), referer=request.headers.get("Referer"),
            http_method=request.method, threat_level=ThreatLevel.HIGH,
            notes="Saldırgan sahte WordPress admin paneline kaba kuvvet (Brute Force) denemesi yaptı."
        )
        hit.populate_datacenter_flag()
        if hit.is_vpn_or_tor: hit.threat_level = ThreatLevel.CRITICAL
        hit.set_fingerprint()
        db.add(hit)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
    
    # Gerçekçi bir wordpress sahte hata ekranı dönüyoruz
    return "<strong>Fatal error:</strong> Call to undefined function wp_signon() in /var/www/html/wp-includes/user.php on line 43", 500

# ── ROUTE 4: STANDART BAL KÜPÜ GİRİŞ NOKTASI (WEB BEACON TRAP) ──────────────
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
                    window.location.href = "/error-page?event=" + "{{ token_id }}";
                }).catch(function() {
                    window.location.href = "/error-page?event=" + "{{ token_id }}";
                });
            };
        </script>
    </head>
    <body style="background-color: #03070c;"></body>
    </html>
    """
    user_agent = request.headers.get("User-Agent", "").lower()
    if any(bot in user_agent for bot in ["curl", "wget", "python", "nikto", "nmap", "sqlmap", "dirb"]):
        db = SessionLocal()
        try:
            hit = CanaryHit(
                token_id=uuid_id, ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"), referer=request.headers.get("Referer"),
                http_method=request.method, threat_level=ThreatLevel.HIGH,
                notes=f"Otomatize Siber Keşif Aracı Engellendi: {user_agent}"
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
        return jsonify({"status": "Access Denied", "code": "SIG_RECON_DETECTED"}), 403

    return render_template_string(telemetry_js_template, token_id=uuid_id)

# ── ROUTE 5: TELEMETRİ ALICI PIPELINE ───────────────────────────────────────
@app.route("/api/v1/telemetry/capture", methods=["POST"])
def telemetry_capture():
    data = request.get_json() or {}
    token_id = data.get("token_id")
    if not token_id: return jsonify({"status": "malformed_payload"}), 400
    
    db = SessionLocal()
    try:
        ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
        if "," in ip_addr: ip_addr = ip_addr.split(",")[0].strip()
        
        hit = CanaryHit(
            token_id=token_id, ip_address=ip_addr,
            user_agent=request.headers.get("User-Agent"), referer=request.headers.get("Referer"),
            http_method="GET", screen_resolution=data.get("screen_resolution"),
            system_languages=data.get("system_languages"), threat_level=ThreatLevel.HIGH
        )
        hit.populate_datacenter_flag()
        if hit.is_vpn_or_tor: hit.threat_level = ThreatLevel.CRITICAL
        hit.set_fingerprint(extra=data.get("screen_resolution", ""))
        db.add(hit)
        db.commit()
        return jsonify({"status": "telemetry_logged"}), 200
    except Exception:
        db.rollback()
        return jsonify({"status": "pipeline_error"}), 500
    finally:
        db.close()

@app.route("/error-page")
def error_page():
    return "<h1>404 Not Found</h1>The requested URL was not found on this server.", 404

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("[+] Taktiksel Siber Savunma Altyapısı Devreye Alındı.")
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
