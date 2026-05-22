import base64
import uuid
from flask import Flask, request, jsonify, render_template_string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from canary_web.models.forensics import Base, CanaryHit, ThreatLevel

app = Flask(__name__)
DATABASE_URI = "sqlite:///canary_dev.db"
engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(bind=engine)

TRANSPARENT_GIF = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")

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

@app.route("/api/v1/tokens/generate", methods=["POST"])
def generate_token():
    generated_uuid = str(uuid.uuid4())
    return jsonify({
        "status": "success",
        "token_id": generated_uuid,
        "trigger_url": f"{request.url_root}t/{generated_uuid}",
        "msg": "Canary token başarıyla oluşturuldu."
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
    if "curl" in user_agent or "wget" in user_agent or "python" in user_agent:
        db = SessionLocal()
        try:
            hit = CanaryHit(
                token_id=uuid_id, ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
                referer=request.headers.get("Referer"), http_method=request.method,
                threat_level=ThreatLevel.HIGH, notes="Terminal (CLI) taraması algılandı."
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
        return jsonify({"error": "Internal Server Error"}), 500

    return render_template_string(telemetry_js_template, token_id=uuid_id)

@app.route("/api/v1/telemetry/capture", methods=["POST"])
def telemetry_capture():
    data = request.get_json() or {}
    token_id = data.get("token_id")
    if not token_id: return jsonify({"status": "error"}), 400
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
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"status": "db_error"}), 500
    finally:
        db.close()

@app.route("/error-page")
def error_page():
    event_id = request.args.get("event", "UNKNOWN")
    return render_template_string(FAKED_ERROR_TEMPLATE, event_id=event_id), 503

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("[+] SQLite Veritabanı ve log tabloları hazır.")
    app.run(host="0.0.0.0", port=5000, debug=True)
