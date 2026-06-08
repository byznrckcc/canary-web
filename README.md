
<p align="center">
  <img src="auth_min_logo.png" alt="Proje Logosu" width="160">
</p>


# 🏫 İSTİNYE ÜNİVERSİTESİ
## 🛡️ Meslek Yüksekokulu // Bilişim Güvenliği Teknolojisi Programı

### 👤 Geliştirici Proje Künyesi
* **Adı Soyadı:** Beyzanur Çakıcı
* **Öğrenci Numarası:** 2420191032
* **Bölüm:** Bilişim Güvenliği Teknolojisi
* **Ders Kodu / Adı:** BGT208 - Güvenli Web Yazılımı Geliştirme
* **Proje Danışmanı / Hocası:** Öğr. Gör. Keyvan Arasteh
* **Kapsam:** Güvenli Web Yazılımı Geliştirme Dönem Final Projesi Ödevi

---
# 🛰️ Canary-Web: Advanced Active Deception & Forensic De-Anonymization Core

> 💡 **PROJE ÖNİZLEMESİ (SOC DASHBOARD)**
> > ![Canary-Web SOC Dashboard](dashboard_ss.png)

Canary-Web; kurumsal ağ altyapılarına, kritik veritabanı sızıntı noktalarına veya API sunucularına sızan sofistike tehdit aktörlerini (Black-Hat Hackers) ve otomatize gelişmiş siber tarama robotlarını (APT) erken aşamada tuzağa düşürmek, izole etmek ve adli bilişim (forensics) kanıtları toplamak amacıyla tasarlanmış **Enterprise-Grade Active Deception (Aldatıcı Siber Savunma)** platformudur.

Sistem, geleneksel pasif bal küpü (honeypot) mantığının ötesine geçerek, saldırganların maskelerini (VPN/Tor/Proxy) tarayıcı katmanında düşüren aktif bir adli bilişim istihbarat mekanizmasına sahiptir.

---

WELL DONE ! :) @keyvanarasteh 

## 🚀 EVDE BAĞIMSIZ TEST VE SİMÜLASYON KILAVUZU 

Bu proje, harici hiçbir dış sunucu bağımlılığı veya karmaşık ağ ayarı gerektirmeden, **tamamen lokal test ortamında (Localhost / Testbed)** bağımsız olarak simüle edilebilecek şekilde "Tak-Çalıştır" mimaride tasarlanmıştır.

Sistemi evinizde canlı olarak test etmek için aşağıdaki 4 siber polisiye adımını takip etmeniz yeterlidir:

### Adım 1: Bağımlılıkların Kurulması ve Hazırlık

Proje klasörünün içinde bir terminal (CLI) açın ve sistem kütüphanelerini tek komutla kurun:

```bash
pip install -r requirements.txt

```

*(Sistem otomatik olarak `Flask`, `SQLAlchemy` ve `python-dotenv` paketlerini kuracaktır).*

### Adım 2: Siber Komuta Merkezinin Ateşlenmesi

Sunucuyu yerel ağ dinleme modunda başlatmak için terminalden şu komutu koşturun:

```bash
python app.py

```

Sunucu `5000` portunda ayağa kalktığında, tarayıcınızdan doğrudan siber harekat merkezine giriş yapın:
👉 **`http://127.0.0.1:5000/dashboard`**

### Adım 3: Yanal Hareket (Lateral Movement) ve Tuzağın Tetiklenmesi

Siber saldırganın sistem sızmasından sonra kritik kimlik bilgilerini aradığını varsaydığımız aşamadır.

* Proje kök dizininde yer alan **`admin_sifreler.txt`** taktiksel yem dosyasını açın.
* İçerisinde kurumsal sistem yöneticisine aitmiş gibi duran sahte bağlantı linkine çift tıklayın (veya tarayıcıda açın):
👉 `http://127.0.0.1:5000/t/db-admin-leak-token`
* Tarayıcı ekranı `0.6` saniye boyunca asenkron adli analiz yapacak ve ardından sizi otomatik olarak Dashboard'a geri atacaktır.

### Adım 4: Adli Kanıtların Mühürlenmesi ve Maske Düşürme

Dashboard ekranına geri döndüğünüzde, sol alttaki gerçek zamanlı tabloya en son tetiklenen log satırı saniyeler içinde düşecektir.

* Tablonun en üstüne düşen **en yeni log satırının üzerine farenizle bir kez tıklayın.**
* Tıkladığınız an sağ taraftaki **AUTOMATED COUNTER-MEASURES MESH** paneli canlanacak; sistem **sizin evinizdeki yerel ağ IP adresinizi (LAN IP)** ve tarayıcınızın GPU'sundan sızdırılan **değişmez donanım kimliğinizi (Hardware ID)** şak diye ekrana basarak kendi maskenizin nasıl düştüğünü canlı kanıtlayacaktır.

---

## 🚨 ÖZEL ANALİZ: "Siber Dedektiflik" & Polis Mantığı Entegrasyonu

Bu proje, bir siber suçlar dedektifinin suçluyu yakalama adımlarını ve "Polis Mantığını" web tabanlı otomatize bir yazılım mimarisine dönüştürür.

| Siber Polis Taktiği | Canary-Web Dijital Karşılığı | Operasyonel Çıktı |
| --- | --- | --- |
| **1. Pusuda Bekleme (Gözlem)** | `/t/<uuid_id>` Aktif İstihbarat Rotası | Kritik kavşakta paket dinleme hattı oluşturma. |
| **2. Telsiz Deşifre (Tercüme)** | *Forensic Parser Engine* Analizi | Ham `User-Agent` verisini siber araç ismine (`Nmap`, `Sqlmap`) çevirme. |
| **3. Davranışsal İnceleme** | Algoritmik Tehdit Risk Skoru | Tehdit aktörünün tehlike endeksini `%0-%100` arası hesaplama. |
| **4. Kelepçeleme (Etkisiz Kılma)** | *Automated Counter-Measures* Hattı | `IPTables DROP`, `Snort Signature` ve `pfSense API` engelleme kodlarını anlık üretme. |

---

## 🌌 İleri Düzey Teknik Yetenekler (Core Features)

* **🎭 WebRTC VPN De-Anonymization (Maske Düşürücü Matrix):** Saldırgan askeri düzeyde şifrelenmiş VPN veya Tor arkasına saklansa bile, tarayıcıların ham WebRTC mimari açığından faydalanarak arka planda görünmez bir asenkron sorgu (`ICE Candidate Leak`) tetikler. Yerel ağdaki (LAN) gerçek iç IP adresini ifşa eder.
* **🧬 Canvas Hardware Fingerprinting (Donanımsal Parmak İzi):** Cihazın ekran kartı motoruna (GPU) görünmez bir 3D grafik çizdirerek gizli sekmeyle bile değişmeyen benzersiz bir **Hardware SHA-256 Hash ID** üretir ve kalıcı takibe alır.
* **📡 Live Cyber Kill-Chain Deception Mapping:** Ön yüze entegre edilen hareketli neon animasyon şeması sayesinde, saldırganın keşif (Recon) aşamasından sızma girişimine kadar olan adımlarını anlık haritalandırır ve izole edildiği (`ISOLATED`) kritik saniyeyi SOC analistine görsel olarak sunar.
* **🧪 Kriptografik Sahte Veri Zehirlemesi (Payload Poisoning):** Tuzağa düşen saldırgana dinamik olarak sahte AWS Cloud Keyleri, kurumsal PostgreSQL şifreleri ve sahte admin JWT token verileri besleyerek (`generate_poisoned_payload`) hacker'ı yanıltır ve siber polise zaman kazandırır.
* **⏳ Oyalama Tuzağı (Active Tarpitting):** Otomatize scriptleri algıladığı an ağ bağlantısını kasıtlı olarak 3.0 saniye geciktirerek saldırganın terminal kaynaklarını sömürür.
* **🔒 OWASP Çevresel Değişken İzolasyonu:** Projenin kriptografik gizli anahtarı (`SECRET_KEY`) kod içerisinden tamamen arındırılmış olup, `python-dotenv` kütüphaneyle `.env` dosyasından hafızaya güvenle yüklenir.

---

## 📂 Proje Klasör Ağacı

Projenin modüler mimarisi, GitHub üzerinde kurumsal standartlarda parçalanmıştır:

```text
canary-web/
├── app.py                     # Kurumsal Çekirdek ve Aktif Savunma Kural Motoru
├── admin_sifreler.txt         # Saldırganı Yanal Harekette Avlayan Taktiksel Yem Dosyası
├── requirements.txt           # Bağımsız Çalıştırma ve Bağımlılık Paket Yönetimi
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

## 👤 Geliştirici Proje Künyesi

* **Adı Soyadı:** Beyzanur Çakıcı
* **Öğrenci Numarası:** 2420191032
* **Bölüm:** Bilişim Güvenliği Teknolojisi
* **Kurum:** İstinye Üniversitesi
* **Ders / Kapsam:** Güvenli Web Geliştirme Final Projesi Ödevi
