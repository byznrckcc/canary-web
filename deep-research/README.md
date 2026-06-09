# 🧬 Canary-Web: İleri Düzey Tarayıcı De-Anonimleştirme ve Aktif Savunma Çekirdek Analizi

**BGT208 - Güvenli Web Yazılımı Geliştirme** dersi kapsamında geliştirilen **Canary-Web** platformunun sömürdüğü tarayıcı açıklarını, donanımsal parmak izi çıkarma algoritmalarını ve adli bilişim (forensics) motorunun low-level çalışma mekanizmalarını inceleyen derin teknik araştırma raporudur.

---

## 🔬 1. WebRTC Protokol Sızıntısı ile Ağ Katmanı İzolasyon Bypass Analizi

Saldırganlar, ağ katmanında kimliklerini gizlemek adına askeri düzeyde şifrelenmiş **VPN** veya **Tor** düğümleri kullansalar dahi, uygulama katmanındaki tarayıcı motorları multimedya akışlarını optimize etmek adına yerel ağ bilgilerini dışarı sızdırabilir.

### 📡 ICE (Interactive Connectivity Establishment) ve SDP Ayrıştırma Mimarisi

**WebRTC** mimarisi, iki tarayıcının birbirine doğrudan (Peer-to-Peer) veri aktarabilmesi için **STUN** sunucularına binding istekleri gönderir.

- **Host Adayları (Host Candidates)**: Tarayıcı, işletim sisteminin ağ arayüzlerini (`getifaddrs()`) sorgulayarak doğrudan cihaza bağlı olan yerel IP adreslerini (`192.168.1.X`, `10.0.0.X`) toplar.
- **Kapsülleme Hatası (TUN/TAP Bypass)**: Birçok ticari VPN yazılımı sadece routing tablosunu manipüle eder. Ancak tarayıcı çekirdeği (Chromium V8 veya Gecko), doğrudan ham soketler üzerinden tüm yerel arayüzleri enumerate ettiği için VPN tünelini bypass ederek ham yerel IP verisini yakalar.

### 💻 Adli Bilişim Veri Toplama Çekirdeği (`telemetry.js`)

```javascript
function performLowLevelWebRTCProbe() {
    return new Promise((resolve, reject) => {
        const rtcConfig = {
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
        };
        const connection = new RTCPeerConnection(rtcConfig);
        
        connection.createDataChannel("canary_forensic_channel");
        connection.createOffer()
            .then(offer => connection.setLocalDescription(offer))
            .catch(err => reject(err));
            
        connection.onicecandidate = (event) => {
            if (!event || !event.candidate) return;
            
            const candidateLine = event.candidate.candidate;
            // Regex: Ham IPv4 adres formatını (RFC 1918) SDP satırlarından izole eder
            const ipPattern = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
            const matchedIP = ipPattern.exec(candidateLine);
            
            if (matchedIP) {
                resolve({
                    rawCandidate: candidateLine,
                    extractedLocalIP: matchedIP[1],
                    candidateType: candidateLine.split(" ")[7] // host, srflx veya relay
                });
                connection.close();
            }
        };
    });
}
```

---

## 🧬 2. Canvas ve WebGL Donanımsal Parmak İzi (Hardware Fingerprinting) ve Matematiksel Entropi Hesaplaması

Siber suçlular IP adreslerini değiştirseler, çerezleri temizleseler veya Incognito Mode kullansalar dahi, donanımsal mikro-mimariyi değiştiremezler.

### 🎨 OS Font Rasterization ve GPU Render Farklılıkları

- **İşletim Sistemi Entropisi**: Windows (DirectWrite), macOS (CoreText) ve Linux (FreeType) farklı anti-aliasing algoritmaları kullanır.
- **GPU Mikro-Mimarisi**: NVIDIA, AMD, Intel ekran kartları render sırasında milisaniyelik ve piksel düzeyinde benzersiz farklılıklar üretir.

**Shannon Entropy** formülü ile benzersizlik hesaplanır:

$$
H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)
$$

### 💻 WebGL Ekran Kartı Kimlik Deşifre Motoru

```javascript
function extractHardwareEntropy() {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) return { error: "WebGL Not Supported" };
    
    // Tarayıcının gizlemeye çalıştığı donanım sürücüsü parametrelerini çeken genişletilmiş API
    const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
    if (debugInfo) {
        const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        return { vendor, renderer }; // Örn: "Intel Inc.", "Intel(R) Iris(TM) Xe Graphics"
    }
    return { error: "Extension Disabled" };
}
```

---

## 🗺️ 3. MITRE ATT&CK® Deception ve Cyber Kill Chain Matrisi Entegrasyonu

Canary-Web, saldırganların **TTP**’lerini manipüle etmek üzere tasarlanmıştır.

| MITRE ATT&CK Taktik / Teknik Kodu | Teknik Adı                          | Canary-Web Karşılığı ve Operasyonel Mantığı |
|------------------------------------|-------------------------------------|---------------------------------------------|
| TA0007 // T1083                   | Discovery // File and Directory Discovery | Saldırganın `/templates` veya root dizindeki kritik dosyaları araması |
| TA0006 // T1552.001               | Credential Access // Credentials in Files | `admin_sifreler.txt` dosyasının sızdırılması |
| TA0008 // T1071.001               | Command and Control // Web Protocols | `/t/<uuid>` Honeytoken rotasına istek |
| Mitigation // M1050               | Deception Deployment                | Sahte sistem kimlikleri ve zehirlenmiş payloadlar ile izole etme |

---

## 📡 4. Siber Tehdit İstihbaratı (CTI) ve STIX v2.1 Yapısal Log Entegrasyonu

Tüm kanıtlar **STIX v2.1** formatında paketlenir ve SIEM/SOAR sistemlerine doğrudan beslenebilir.

### 📄 Gerçek Zamanlı Üretilen Kurumsal İstihbarat Paketi (STIX Payload)

```json
{
  "type": "bundle",
  "id": "bundle--8f6a394c-e123-4cbb-9bfb-2c4f1c1f728c",
  "spec_version": "2.1",
  "objects": [
    {
      "type": "indicator",
      "id": "indicator--bf4a2420-1910-32cf-bgt2-08secureweb",
      "created": "2026-06-09T18:00:00.000Z",
      "pattern": "[ipv4-addr:value = '127.0.0.1'] AND [file:name = 'admin_sifreler.txt']",
      "pattern_type": "stix",
      "valid_from": "2026-06-09T18:00:00.000Z",
      "indicator_types": ["malicious-activity", "compromised-credentials"]
    },
    {
      "type": "observed-data",
      "id": "observed-data--5c5c9a1d-4444-4a4a-9a9a-canaryweb99",
      "first_observed": "2026-06-09T18:00:00.000Z",
      "last_observed": "2026-06-09T18:00:00.000Z",
      "number_of_observed_data": 1,
      "objects": {
        "0": {
          "type": "user-account",
          "user_id": "Honeytoken_Trapper_Triggered",
          "x_hardware_fingerprint_sha256": "8a39b23f8c8111e89b2c4f1c1f728cb11394fde182cbde91032bf4a242019103"
        }
      }
    }
  ]
}
```

---

## 🧪 5. Active Tarpitting (Oyalama Tuzağı) ve TCP/HTTP Katmanında Kaynak Tüketimi

Saldırgan bot (requests, Nikto, Dirbuster vb.) tespit edildiğinde devreye giren **Active Tarpitting** mekanizması:

- HTTP yanıt başlıklarını kasıtlı olarak geciktirir.
- TCP pencere manipülasyonu ile bağlantıyı açık tutar.
- Saldırganın kendi CPU/RAM kaynaklarını tüketerek diğer hedefleri taramasını engeller.

---

**Hazırlayan:** Canary-Web Geliştirme Ekibi  
**Tarih:** 9 Haziran 2026  
**Ders:** BGT208 - Güvenli Web Yazılımı Geliştirme
