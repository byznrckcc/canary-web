# 🛰️ Canary-Web: Active Cyber Deception & Forensic Telemetry Infrastructure

Canary-Web, kurumsal web altyapılarına sızan tehdit aktörlerini ve otomatize keşif robotlarını erken aşamada tuzağa düşürmek, izole etmek ve adli bilişim (forensics) kanıtları toplamak amacıyla tasarlanmış **Enterprise-Grade Active Deception (Aldatıcı Siber Savunma)** platformudur.

Bu proje, **İstinye Üniversitesi Bilişim Güvenliği Teknolojisi** bölümü **Güvenli Web Geliştirme** dersi final gereksinimleri doğrultusunda, sıkılaştırılmış güvenli kodlama mimarilerine (OWASP Top 10) tam uyumlu olarak modüler bir yapıda inşa edilmiştir.

---

## 🌌 Mimari Tasarım ve İleri Düzey Yetenekler

### 1. Siber Polis Seviyesi Adli Deşifre Motoru (Forensic Parser Engine)
Saldırganların veya otomatize zafiyet tarayıcılarının sisteme bıraktığı HTTP parmak izleri (User-Agent) ham paket seviyesinde analiz edilir. Statik regex veya düz mantık yerine, akıllı bir ayrıştırıcı yardımıyla saldırganın tam işletim sistemi (Kali Linux, Windows 11, Ubuntu Enterprise) ve kullandığı siber tarama aracı (Nmap, Sqlmap, Nikto, Dirb, curl) nokta atışı tespit edilerek yönetim paneline yansıtılır.

### 2. Aktif Hacker Oyalama Tuzağı (Active Tarpitting)
Profesyonel hackerlar sızdıkları ağdaki linklerin bir honeypot (bal küpü) olup olmadığını sunucunun yanıt hızından ölçebilirler. Canary-Web, otomatize siber saldırı araçlarını tespit ettiği an ağ bağlantısını koparmak veya standart bir hata kodu dönmek yerine **Asenkron Yavaşlatma Tuzağı** uygular. İstekleri kasıtlı olarak 3.0 saniye geciktirerek saldırganın terminal kaynaklarını sömürür ve sistemin gerçek bir kurumsal sunucu yavaşlığı olduğuna inanmasını sağlar.

### 3. Kriptografik Veri Zehirlemesi (Honey-Payload Poisoning)
Tarpit tuzağına düşen saldırgana boş veri döndürülmez. `generate_poisoned_payload()` motoru vasıtasıyla dinamik ve rastgele üretilen sahte AWS Cloud Access Keyleri, kurumsal PostgreSQL veritabanı bağlantı dizgileri ve sahte admin JWT tokenları saldırgana enjekte edilir. Saldırgan gerçek veri sızdırdığını sanıp bu sahte şifreleri kırmaya çalışırken, siber olay müdahale ekiplerine (SOC) kritik bir zaman kazandırılmış olur.

### 4. Uluslararası Siber Tehdit İstihbaratı Entegrasyonu (STIX v2.1 Standard)
Toplanan adli bilişim artifacts verileri sadece yerel log olarak tutulmaz. Siber suçlarla mücadele ekiplerinin ve global siber operasyon merkezlerinin kullandığı resmi tehdit paylaşım dili olan **STIX v2.1 JSON** formatına kriptografik olarak base64 katmanıyla dönüştürülür.

---

## 🔒 Güvenli Kodlama ve OWASP Sıkılaştırma Raporu

* **HTTP Security Headers:** Sunucu üzerinden yayılan tüm yanıtlar `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` ve `X-XSS-Protection` kuralları ile zırhlandırılmıştır.
* **Content Security Policy (CSP):** Zararlı satır içi betik çalıştırma (XSS) saldırılarını engellemek adına katı içerik güvenlik politikaları uygulanmıştır.
* **Asenkron Non-Blocking Queue Altyapısı:** Olası bir siber saldırı veya log yoğunluğu durumunda Flask ana motorunun kilitlenmesini engellemek için adli bilişim logları arka planda bağımsız thread'ler yöneten bir `Queue` mimarisiyle veri tabanına işlenir.
* **SAST & Linting:** Proje kaynak kodları siber güvenlik zafiyet tarayıcı kuralları içeren `ruff.toml` (Bandit/SAST) kuralları ile sürekli denetlenmektedir.

---

## 📂 Proje Klasör Ağacı ve Çoklu Dil Footprint'i

Projenin modüler mimarisi, GitHub üzerinde zengin bir dil dağılım matrisi (Python, JavaScript, CSS, Shell Script) oluşturacak şekilde kurumsal standartlarda parçalanmıştır:

```text
canary-web/
├── app.py                     # Kurumsal Çekirdek ve Aktif Savunma Kural Motoru
├── ruff.toml                  # SAST Statik Kod Analizi Güvenlik Yapılandırması
├── healthcheck.sh             # Konteyner Sağlık Koruma ve Adli Yaşam Döngüsü Betiği
├── static/
│   ├── css/
│   │   └── cyberpunk.css      # OffSec Esintili Yüksek Kontrastlı Taktiksel Stil Dosyası
│   └── js/
│       └── telemetry.js       # Adli Bilişim DOM Etkileşim ve Kilitlenme Çözücü JS Motoru
└── templates/
    └── dashboard.html         # Siber Operasyon Komuta Merkezi (SOC) Arayüzü

    🛠️ Kurulum ve Canlı Çalıştırma

    Proje bağımlılıklarını sisteminize entegre edin:
    Bash

pip install Flask SQLAlchemy

Sistemi yerel ağ üzerinde dinleme modunda başlatın:
Bash

python app.py

Yönetim panelini ve siber izleme ekranını tarayıcınızda başlatın:
Plaintext

    [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

👤 Geliştirici Proje Künyesi

    Adı Soyadı: Beyzanur Çakıcı

    Öğrenci Numarası: 2420191032

    Bölüm: Bilişim Güvenliği Teknolojisi

    Kurum: İstinye Üniversitesi // Güvenli Web Geliştirme Final Projesi Ödevi


