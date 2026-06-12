# ⚙️ Config Lab: Altyapı ve Sunucu Sıkılaştırma (Hardening) Kılavuzu
## 📌 Konu: PHP, Next.js, Docker, Nginx, cPanel ve VPS Katmanlarında Üretim Ortamı Güvenliği

---

## 🔒 1. Güvenli Nginx Konfigürasyonu (`nginx.conf`)

```nginx
# Server bilgilerini HTTP başlıklarından gizler
server_tokens off;

# Gelişmiş Güvenlik Başlıkları Entegrasyonu
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;

# Sadece Güvenli TLS Sürümleri
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';

# DoS/DDoS Saldırılarına Karşı Hız Sınırlandırma
client_max_body_size 2m;
limit_req_zone $binary_remote_addr zone=ddos_defense:10m rate=5r/s;
## 🐋 2. Sertleştirilmiş Dockerfile Yapısı

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# 🔥 Root kullanıcısını devre dışı bırakıp 'node' kullanıcısına geçiş
USER node

EXPOSE 3000
CMD ["npm", "start"]
; PHP versiyon bilgisinin dışarıya sızmasını engeller
expose_php = Off

; Terminal komutu çalıştırabilecek tehlikeli fonksiyonları tamamen yasaklar
disable_functions = exec, passthru, shell_exec, system, proc_open, popen, curl_multi_exec, show_source, eval, assert

; Hata mesajlarının tarayıcıya basılmasını engeller (Log dosyasına yazar)
display_errors = Off
log_errors = On
error_log = /var/log/php/error.log

; Uzaktan dosya dahil etme (RFI) saldırılarını engeller
allow_url_fopen = Off
allow_url_include = Off

; Oturum (Session) Güvenliği Çerez Sıkılaştırması
session.cookie_httponly = On
session.cookie_secure = On
session.cookie_samesite = "Strict"
# IP Spoofing ve Sahte Paket Saldırılarını Önleme
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# DoS/SYN Flood Ataklarına Karşı SYN Çerez Desteği
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048

# Ağ Haritası Çıkarılmasını Engelleme (ICMP Kapatma)
net.ipv4.conf.all.accept_redirects = 0
Port 2222                 # Standart 22 portunu değiştiriyoruz
PermitRootLogin no        # Root kullanıcısının doğrudan SSH yapmasını yasaklıyoruz
PasswordAuthentication no # Sadece kriptografik SSH Key ile girişe izin veriyoruz
MaxAuthTries 3            # Üst üste 3 kez hatalı deneme yapanı düşürür
