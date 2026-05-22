# 🎯 Honeytoken Algılama ve Adli Bilişim (Forensics) Analiz Kılavuzu

Bu kılavuz, **Canary-Web** projesinin siber aldatmaca (cyber deception) ve adli veri analitiği süreçlerini, Keyvan Hoca'nın "Önce Anla, Sonra Kodla" felsefesine uygun olarak adım adım parçalara ayırarak açıklar.

---

## 🧭 Bölüm 1: Temel Kavramlar
1. **Cyber Deception (Aldatıcı Teknolojiler):** Saldırganları engellemeye çalışmak yerine, sistem içerisine cazip ama sahte varlıklar bırakarak onları tuzağa çekme stratejisidir.
2. **Honeytoken (Bal Küpü Varlık):** İçerisinde gerçek veri barındırmayan ancak yetkisiz bir aktör dokunduğu an (tıkladığında/açtığında) sinyal üreten dijital mayınlardır.
3. **Web Beacon (Web İşaretçisi):** Bir HTML kodunun veya dokümanın içine gizlenmiş, görünmez 1x1 piksellik nesneler veya tetikleyici URL adresleridir.
4. **Browser Fingerprinting (Tarayıcı Parmak İzi):** Saldırgan IP adresini değiştirse bile, cihazın ekran boyutu, işletim sistemi dili ve donanım bileşenleri üzerinden o cihazın kimliğini benzersiz şekilde tanımlama yöntemidir.

---

## ⚙️ Bölüm 2: Nasıl Çalışır? (Teknik Akış)
Sistem, karmaşık ağ hareketlerini 4 temel mikro adıma bölerek takip eder:
* **Adım A (Üretim):** Sistem yöneticisi panelden benzersiz bir izleme kimliği (`UUIDv4`) üretir.
* **Adım B (Konumlandırma):** Bu kimliğe bağlı link (`/t/<uuid>`), sistemde saldırganın ilk sızabileceği kritik dosyalara (Örn: `config_backup.php`) yerleştirilir.
* **Adım C (Tetiklenme & Yakalama):** Saldırgan dosyayı okuduğunda tarayıcı veya terminal üzerinden Flask motoruna bir `GET` isteği düşer.
* **Adım D (Raporlama):** Ağ katmanı verileri (IP, User-Agent) ve cihaz verileri (Ekran, Dil) SQLite veritabanına işlenerek SOC Dashboard'a canlı aktarılır.

---

## ⚠️ Bölüm 3: Tehdit mi, Değil mi? (Anomali Tespiti)
Gelen her bağlantı doğrudan tehlike olarak yorumlanmaz. Sistem akıllı kural motoruyla ayrım yapar:
* **Normal Trafik:** İç ağdaki yetkili personelin kazara erişimleri veya sistemin kendi döngüleri (Düşük Tehdit).
* **Anormal Trafik (Zafiyet/Keşif Taraması):** Milisaniyeler içinde gelen otomatize CLI araçları (`curl`, `wget`, `python-requests`) istekleri doğrudan keşif (recon) faaliyeti olarak etiketlenir.
* **Kritik Tehdit (Sızma Girişimi):** Eğer gelen istek AWS, Azure, DigitalOcean gibi bilinen bulut sunucu IP adreslerinden (Datacenter CIDR) veya VPN/Tor ağlarından geliyorsa tehdit seviyesi anında **CRITICAL** olarak güncellenir.

---

## 📊 Bölüm 4: Ne Bilgiler Gider? (Adli Veri Analizi)
Sistem, bir siber olay müdahale (IR) uzmanının ihtiyaç duyacağı şu ham verileri (evidence) toplar ve deşifre eder:
* **IP Adresi & Ağ Katmanı:** Saldırganın ağdaki çıkış noktası (`X-Forwarded-For` korumalı).
* **User-Agent String:** Saldırganın kullandığı tarayıcı veya saldırı aracı (Örn: `Sqlmap`, `Nmap`, `Mozilla`).
* **Ekran Çözünürlüğü & Sistem Dili:** İstemci tarafında asenkron çalışan betik sayesinde saldırganın fiziksel ekran boyutları ve yerel işletim sistemi dili.
* **Kriptografik Cihaz Hash'i:** Toplanan tüm donanımsal metadataların SHA-256 algoritmasından geçirilerek elde edilen deterministik cihaz izi.

---

## 🛡️ Bölüm 5: Nasıl Korunuruz? (Mitigation)
Honeytoken sistemleri tek başına bir koruma duvarı değildir; bir erken uyarı alarmıdır. Sistem bir tehdit algıladığında savunma hattı şu adımları atar:
1. **Aldatıcı Yönlendirme:** Saldırganın sistemde açık bulduğunu sanıp sevinmesini engellemek için doğrudan sahte bir `503 Service Unavailable` sayfası gösterilerek dikkat dağıtılır.
2. **SOC Entegrasyonu:** Güvenlik operasyon merkezi panelinde parlayan kırmızı alarmla sistem yöneticisi uyarılır.
3. **Firewall Kuralı Tetikleme (Gelecek Planı):** Tespit edilen zararlı parmak izine veya veri merkezi IP'sine ait ağ trafiğinin güvenlik duvarı (Firewall) üzerinden otomatik olarak engellenmesi (Drop) sağlanır.

---

## 🕵️‍♂️ Bölüm 6: Siber Dedektiflik Özeti (Polis Mantığı)

Keyvan Hoca'nın siber olay analizi için belirttiği **"Polis-Suçlu Dedektiflik Mantığı"** Canary-Web sisteminde tam olarak şu mimari bileşenlere denk gelmektedir:

| Polis Mantığı Kavramı | Canary-Web Sistemindeki Karşılığı | Teknik Açıklama |
| :--- | :--- | :--- |
| **Olay Yeri (Network Interface)** | `/t/<uuid_id>` Giriş Tuzağı Endpoint'i | Saldırganın tuzağa bastığı, ağ trafiğinin dinlendiği gözlem noktası. |
| **Delil (Raw Packets)** | Ham HTTP Header'ları ve JSON Gövdesi | İstekle birlikte gelen deşifre edilmemiş ham IP, User-Agent ve referer byte'ları. |
| **Tercüman (Deşifre Motoru)** | Flask Router & Parser Hattı | Gelen ham byte'ları anlamlı verilere (ekran çözünürlüğü, tarayıcı tipi) çeviren katman. |
| **Kanıt (Anormal Desen / İmza)** | Datacenter CIDR Blokları & SHA-256 Hash | IP'nin bulut sağlayıcı çıkışlı olması ve cihaz parmak izinin aynı saldırganla eşleşmesi. |
| **Tutuklama (Kaynak Engelleme)** | SOC Dashboard Alarmı & 503 Yanıltması | Tehdidin panelde ifşa edilmesi ve saldırganın sahte sayfaya hapsedilerek durdurulması. |

---
*Bu kılavuz İstinye Üniversitesi Bilişim Güvenliği Teknolojisi Bölümü Güvenli Web Geliştirme Dersi final projesi teorik altyapısı için hazırlanmıştır.*
