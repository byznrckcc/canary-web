

# 🛰️ Canary-Web: Advanced Active Deception & Forensic De-Anonymization Core
![Canary-Web Tactical Core Banner](https://img.shields.io/badge/Security-OWASP%20Top%2010%20Hardened-6366f1?style=for-the-badge&logo=target&logoColor=white)

Canary-Web; kurumsal ağ altyapılarına, kritik veritabanı sızıntı noktalarına veya API sunucularına sızan sofistike tehdit aktörlerini (Black-Hat Hackers) ve otomatize gelişmiş siber tarama robotlarını (APT) erken aşamada tuzağa düşürmek, izole etmek ve adli bilişim (forensics) kanıtları toplamak amacıyla tasarlanmış **Enterprise-Grade Active Deception (Aldatıcı Siber Savunma)** platformudur.

Sistem, geleneksel pasif bal küpü (honeypot) mantığının ötesine geçerek, saldırganların maskelerini (VPN/Tor/Proxy) tarayıcı katmanında düşüren aktif bir adli bilişim istihbarat mekanizmasına sahiptir.

---

## 🚨 ÖZEL ANALİZ: "Siber Dedektiflik" & Polis Mantığı Entegrasyonu

Bu proje, bir siber suçlar dedektifinin suçluyu yakalama adımlarını ve "Polis Mantığını" web tabanlı otomatize bir yazılım mimarisine dönüştürür. 

### 1. Nerede Durman Lazım? (Gözlem Noktası)

* **Polis Dedektifliği:** Ağ trafiğinin geçtiği kritik bir noktada (localhost, gateway veya sunucu önü) konumlanarak Wireshark veya tcpdump gibi sokak köşesinde pusuda beklemek.
* **Canary-Web Entegrasyonu:** Sistem, ağın en kritik ve saldırgana çekici gelen bal küpü rotasında (`/t/<uuid_id>`) konumlanır. Bir ağ kartı gibi gelen tüm HTTP paket isteklerini pusuda bekleyerek sessizce dinler.

### 2. Neleri Çevirmen Lazım? (Deşifre)

* **Polis Dedektifliği:** Ham veriyi okumak, port numaralarını (80/443 HTTP) çevirmek, IP adreslerini çözerek kime ait olduğunu, ülkesini, VPN durumunu bulmak ve zaman damgalarını bağlamak.
* **Canary-Web Entegrasyonu:** Gelen isteklerin ham `User-Agent` ve paket başlıklarını okur. Entegre coğrafi istihbarat simülatörü (`analyze_ip_intelligence`) ile IP'nin hangi ülkeye ait olduğunu, ASN ağ sağlayıcısını, veri merkezinden gelip geçmediğini ve tam UTC zaman damgasıyla veri tabanına işler.

### 3. Çevirince Neyi İnceleyeceksin? (Tespit & Tehdit Analizi)

* **Polis Dedektifliği:** Anormallik aramak, port tarama desenlerini yakalamak, banner toplama girişimlerini izlemek, bilinen saldırı imzalarını (signature) denetlemek ve davranışsal analiz yapmak.
* **Canary-Web Entegrasyonu:** Gelişmiş adli deşifre motoru (`parse_forensic_intelligence`) sayesinde isteklerin normal bir kullanıcı mı yoksa `Nmap`, `Sqlmap`, `Nikto` veya `curl` gibi otomatize bir siber silah mı olduğunu saniyeler içinde analiz eder. Algoritmik Tehdit Skoru ile saldırganın risk endeksini (%0-%100) hesaplar.

### 4. Polis Mantığıyla Özet Sinerjisi (The Cyber Forensics Matrix)

Adli bilişim matrisi sistem arayüzünde şu şekilde vücut bulur:

* **Olay Yeri:** Ağ trafiğinin geçtiği bal küpü web arayüz noktası (`/t/<uuid_id>`).
* **Delil:** Gelen/giden ham paketlerden sızdırılan tarayıcı meta dataları, çözünürlük ve dil parametreleri.
* **Tercüman:** Ham `User-Agent` string'lerini anlamlı siber araç isimlerine dönüştüren *Forensic Parser Engine* ve verinin uluslararası dili olan *STIX v2.1 CTI Compiler*.
* **Kanıt:** Algılanan anormal tarama desenleri, risk skorları ve de-anonim edilmiş gerçek kimlikler.
* **Tutuklama:** Tespit edilen anomalinin SOC paneline raporlanması, `IPTables DROP` kurallarının, `Snort Drop` imzalarının ve `pfSense API` bloklama payload'larının anında otomatik üretilerek kaynağın engellenmesi.

---

## 🌌 İleri Düzey Teknik Yetenekler (Core Features)

* **🎭 WebRTC VPN De-Anonymization (Maske Düşürücü Matrix):** Saldırgan askeri düzeyde şifrelenmiş VPN veya Tor arkasına saklansa bile, tarayıcıların ham WebRTC mimari açığından faydalanarak arka planda görünmez bir asenkron sorgu (ICE Candidate Leak) tetikler. Yerel ağdaki (LAN) gerçek iç IP adresini (Örn: `192.168.1.105`) ifşa eder.
* **🧬 Canvas Hardware Fingerprinting (Donanımsal Parmak İzi):** Cihazın ekran kartı motoruna (GPU) görünmez bir 3D grafik çizdirerek gizli sekmeyle bile değişmeyen benzersiz bir **Hardware SHA-256 Hash ID** üretir ve kalıcı takibe alır.
* **🧪 Kriptografik Sahte Veri Zehirlemesi (Payload Poisoning):** Tuzağa düşen saldırgana dinamik olarak sahte AWS Cloud Keyleri, kurumsal PostgreSQL şifreleri ve sahte admin JWT token verileri besleyerek (`generate_poisoned_payload`) hacker'ı yanıltır ve siber polise zaman kazandırır.
* **⏳ Oyalama Tuzağı (Active Tarpitting):** Otomatize scriptleri algıladığı an ağ bağlantısını kasıtlı olarak 3.0 saniye geciktirerek saldırganın terminal kaynaklarını sömürür.

---

## 📂 Proje Klasör Ağacı ve Çoklu Dil Footprint'i

Projenin modüler mimarisi, GitHub üzerinde zengin bir yazılım dil dağılım matrisi oluşturacak şekilde kurumsal standartlarda parçalanmıştır:

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

```

---

## 🛠️ Kurulum ve Canlı Çalıştırma

Platformun bağımlılıklarını kurmak ve siber savunma ağını devreye almak için sırasıyla aşağıdaki komut mimarisini takip edin:

```bash
pip install Flask SQLAlchemy

```

Sistemi yerel ağ üzerinde dinleme modunda başlatın:

```bash
python app.py

```

Yönetim panelini ve siber istihbarat izleme ekranını görüntülemek için tarayıcınızdan aşağıdaki yerel ağ rotasına erişim sağlayın:

```plaintext
http://127.0.0.1:5000/dashboard

```

---

## 👤 Geliştirici Proje Künyesi

* **Adı Soyadı:** Beyzanur Çakıcı
* **Öğrenci Numarası:** 2420191032
* **Bölüm:** Bilişim Güvenliği Teknolojisi
* **Kurum:** İstinye Üniversitesi
* **Ders / Kapsam:** Güvenli Web Geliştirme Final Projesi Ödevi
