import base64
import os
import logging
from logging.handlers import RotatingFileHandler
import uuid
from flask import Flask, request, jsonify, render_template_string, render_template
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from canary_web.models.forensics import Base, CanaryHit, ThreatLevel

# ── 1. MERKEZİ YAPILANDIRMA (CONFIGURATION) ─────────────────────────────────
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "canary_web_secure_fallback_key_2026")
    DATABASE_URI = "sqlite:///canary_dev.db"
    DEBUG = True
    PORT = 5000
    HOST = "0.0.0.0"

app = Flask(__name__)
app.config.from_object(Config)

# ── 2. ENDÜSTRİYEL LOGLAMA ALTYAPISI (LOGGING) ──────────────────────────────
log_handler = RotatingFileHandler('canary_system.log', maxBytes=1000000, backupCount=3)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger("CanaryWebLogger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Veritabanı Bağlantısı
engine = create_engine(app.config["DATABASE_URI"], echo=False)
SessionLocal = sessionmaker(bind=engine)

# Standart 1x1 Şeffaf GIF (Web Beacon)
TRANSPARENT_GIF = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")

# Sahte Hata Sayfası Şablonu
FAKED_ERROR_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>503 Service Unavailable</title>
    <style>
        body { background-color: #f1f1f1; color: #555; font-family: sans-serif; text-align: center; padding-top: 150px; }
        h1 { font-size: 40px; color: #333; }
        p { font-size: 18px; }
        .code { color: #999; font-family: monospace; }
    </style>
</head>
<body>
    <h1>Sunucu Geçici Olarak Hizmet Dışı</h1>
    <p>İstenen kaynak üzerinde planlı bakım çalışması yapılmaktadır. Lütfen daha sonra tekrar deneyiniz.</p>
    <p class="code">Error Code: HTTP 503 Service Unavailable (ID: {{ event_id }})</p>
</body>
</html>
"""

# ── 3. GÜVENLİK BAŞLIKLARI MIDDLEWARE (SECURE HEADERS) ───────────────────────
@app.after_request
def inject_security_headers(response):
    """
    Güvenli Web Geliştirme standartlarına uygun olarak, her HTTP yanıtına
    OWASP tarafından önerilen kritik güvenlik başlıklarını enjekte eder.
    """
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net;"
    response.headers["Server"] = "Secure-Audit-Server"  # Banner Grabbing saldırılarını yanıltmak için
    return response

# ── 4. MERKEZİ HATA YÖNETİMİ (GLOBAL EXCEPTION HANDLING) ────────────────────
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 Not Found tetiklendi: {request.path} - IP: {request.remote_addr}")
    return jsonify({"error": "Resource not found", "status": 404}), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 Internal Server Error: {str(e)}")
    return jsonify({"error": "Internal server configuration anomaly", "status": 500}), 500

# ── 5. UYGULAMA ROTASI: ADMIN DASHBOARD ─────────────────────────────────────
@app.route("/dashboard", methods=["GET"])
def dashboard_view():
    db = SessionLocal()
    try:
        all_hits = db.query(CanaryHit).order_by(CanaryHit.created_at.desc()).all()
        total_hits = len(all_hits)
        critical_hits = db.query(CanaryHit).filter(CanaryHit.threat_level == ThreatLevel.CRITICAL).count()
        unique_tokens = db.query(func.count(CanaryHit.token_id.distinct())).scalar() or 0
        
        return render_template(
            "dashboard.html", 
            hits=all_hits, total_hits=total_hits, 
            critical_hits=critical_hits, unique_tokens=unique_tokens
        )
    except Exception as e:
        logger.error(f"Dashboard yüklenirken kritik DB hatası: {str(e)}")
        return "System Integrity Error", 500
    finally:
        db.close()

# ── 6. UYGULAMA ROTASI: TOKEN ÜRETİCİ (GENERATOR) ────────────────────────────
@app.route("/api/v1/tokens/generate", methods=["POST"])
def generate_token():
    generated_uuid = str(uuid.uuid4())
    logger.info(f"Yeni Canary Token üretildi: {generated_uuid} - Kaynak IP: {request.remote_addr}")
    return jsonify({
        "status": "success",
        "token_id": generated_uuid,
        "trigger_url": f"{request.url_root}t/{generated_uuid}",
        "msg": "Canary token başarıyla oluşturuldu ve şifrelendi."
    }), 201

# ── 7. UYGULAMA ROTASI: BAL KÜPÜ GİRİŞ NOKTASI (TRIGGER) ─────────────────────
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
    <body style="background-color: #ffffff;"></body>
    </html>
    """
    user_agent = request.headers.get("User-Agent", "").lower()
    
    # CLI / Bot taraması algılama mekanizması
    if any(bot in user_agent for bot in ["curl", "wget", "python", "nikto", "nmap", "sqlmap"]):
        logger.warning(f"Otomatize tarama aracı tespit edildi! Araç: {user_agent} - IP: {request.remote_addr}")
        db = SessionLocal()
        try:
            hit = CanaryHit(
                token_id=uuid_id, ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
                referer=request.headers.get("Referer"), http_method=request.method,
                threat_level=ThreatLevel.HIGH, notes=f"CLI/Bot Taraması Bloklandı: {user_agent}"
            )
            hit.populate_datacenter_flag()
            if hit.is_vpn_or_tor: hit.threat_level = ThreatLevel.CRITICAL
            hit.set_fingerprint()
            db.add(hit)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"CLI loglama hatası: {str(e)}")
        finally:
            db.close()
        return jsonify({"error": "Internal Server Error"}), 500

    return render_template_string(telemetry_js_template, token_id=uuid_id)

# ── 8. UYGULAMA ROTASI: ADLİ VERİ ANALİZ PIPELINE (CAPTURE) ──────────────────
@app.route("/api/v1/telemetry/capture", methods=["POST"])
def telemetry_capture():
    data = request.get_json() or {}
    token_id = data.get("token_id")
    if not token_id: return jsonify({"status": "error", "message": "Missing Payload"}), 400
    
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
        if hit.is_vpn_or_tor: 
            hit.threat_level = ThreatLevel.CRITICAL
            logger.critical(f"KRİTİK TEHDİT: Veri Merkezi veya VPN üzerinden erişim! IP: {ip_addr}")
        
        hit.set_fingerprint(extra=data.get("screen_resolution", ""))
        db.add(hit)
        db.commit()
        logger.info(f"Adli bilişim kanıtı başarıyla kaydedildi. Token: {token_id} - IP: {ip_addr}")
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        db.rollback()
        logger.error(f"Telemetri capture hatası: {str(e)}")
        return jsonify({"status": "db_error"}), 500
    finally:
        db.close()

@app.route("/error-page")
def error_page():
    event_id = request.args.get("event", "UNKNOWN")
    return render_template_string(FAKED_ERROR_TEMPLATE, event_id=event_id), 503

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    logger.info("Canary-Web Enterprise Backend Core Engine successfully initialized.")
    print("[+] Kurumsal Seviye Flask Motoru ve Güvenlik Altyapısı Hazır.")
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
