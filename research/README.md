# 🔬 Analiz Laboratuvarı: Vercel Tedarik Zinciri İhlali Analiz Raporu
## 📌 Vaka: Context.ai OAuth İstismarı Üzerinden Vercel Sızıntısı (Şubat - Nisan 2026)

* **Etki Skoru (Impact):** 98/100
* **Saldırı Türü (Attack Type):** Tedarik Zinciri Güvenliği (Supply Chain / OAuth Trust Exploitation)
* **İlk Giriş Vektörü (Initial Vector):** Bilgi Çalıcı Zararlı Yazılım (InfoStealer Malware - Lumma Stealer)
* **İfşa Edilen Veriler (Data Exposed):** Şifrelenmemiş / Hassas İşaretlenmemiş Ortam Değişkenleri (Environment Variables)
* **CVE Kodu:** Yok (Mantıksal Güven Zinciri İstismarı / Logic)

---

## 🧭 1. Tam Saldırı Zinciri (Full Attack Chain Mimarisi)

Saldırı, klasik bir kod tabanı veya paket açığına dayanmamış, insan faktöründen başlayarak bulut ve yetkilendirme katmanlarına kadar uzanan domino etkisiyle gerçekleşmiştir:

```text
[Roblox Exploit Betikleri] ──> [Lumma Stealer Enfeksiyonu] ──> [Context.ai Çalışan Cihazı]
                                                                        │
[Vercel Dahili Sistemlerine Pivot] <── [Google Workspace Ele Geçirme] <── [AWS Ortamından OAuth Çalınması]
                │
[Hassas Olmayan Müşteri Env Var İfşası] ──> [ShinyHunters $2M Veritabanı Satış İddiası]
## 📅 2. Detaylı Saldırı Zaman Çizelgesi (Timeline)

### 🔴 Şubat 2026 - İlk Ele Geçirme (Lumma Stealer Enfeksiyonu)
Bir Context.ai çalışanı cihazına Roblox oyun exploit betikleri indirir ve farkında olmadan Lumma Stealer infostealer zararlı yazılımını yükler. Zararlı yazılım cihazdan tarayıcıda saklanan kimlik bilgilerini, oturum çerezlerini ve OAuth tokenlarını toplar.

### 🔴 Mart 2026 - Context.ai AWS Ortamı İhlal Edildi
Çalınan kimlik bilgilerini kullanarak saldırgan Context.ai'nin AWS ortamına yetkisiz erişim sağlar. Context.ai'nin "AI Office Suite" tüketici ürünü kullanıcılarına ait OAuth tokenlarını çıkarır — bunlardan biri "Tümüne İzin Ver" Google Workspace izinleri vermiş bir Vercel çalışanına aittir.

### 🟡 Mart 2026 - İzinsiz Girişin Tespiti (Detected)
Context.ai bağımsız olarak AWS ortamına yetkisiz erişimi tespit eder ve saldırganın oturumunu sonlandırır. Ancak çıkarılan OAuth tokenları zaten saldırganın elindedir.

### 🔴 Mart – Nisan 2026 - Vercel'e Yanal Hareket (Lateral Movement)
Saldırgan çalınan Vercel çalışan OAuth tokenını kullanarak Google Workspace hesabına erişir, ardından Vercel dahili sistemlerine ve panolara pivot yapar. "Hassas" olarak işaretlenmemiş müşteri ortam değişkenlerini numaralandırır.

### 🔵 19 Nisan 2026 - Vercel Kamuya Açıklama
Vercel güvenlik olayını kamuya açıklar. Dahili sistemlere yetkisiz erişimi ve hassas olmayan ortam değişkenlerinin potansiyel ifşasını doğrular. Olay müdahalesi için Mandiant (Google) görevlendirilir.

### 🔵 Nisan 2026 - ShinyHunters İddiası ve Kimlik Bilgisi Döndürme
Tehdit aktörü "ShinyHunters" sorumluluğu üstlenir ve sözde Vercel veritabanı verilerini 2 milyon dolara satmaya çalışır — atıf doğrulanmamıştır. Vercel tüm müşterilerden hassas olmayan env değişkenlerinde saklanan sırları döndürmelerini ister.
## 🛠️ 3. Keşif ve Tarama Teknikleri (Reconnaissance & Scanning)

### A. Alt Alan Adı ve Varlık Keşfi (Asset Discovery)
Vercel üzerinde barındırılan tüm alan adlarını haritalamak için Amass, Subfinder ve crt.sh kullanılır:
```bash
subfinder -d target.com -o subdomains.txt
amass enum -d target.com
curl "[https://crt.sh/?q=%.target.com&output=json](https://crt.sh/?q=%.target.com&output=json)" | jq .
trufflehog git [https://github.com/org/repo](https://github.com/org/repo) --json
gitleaks detect --source=. --report-format=json
