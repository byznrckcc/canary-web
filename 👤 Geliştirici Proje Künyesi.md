🧬 Canary-Web: İleri Düzey Tarayıcı De-Anonimleştirme ve Aktif Savunma Çekirdek Analizi

Bu döküman, BGT208 - Güvenli Web Yazılımı Geliştirme dersi kapsamında geliştirilen Canary-Web platformunun sömürdüğü tarayıcı açıklarını, donanımsal parmak izi çıkarma algoritmalarını ve adli bilişim (forensics) motorunun low-level çalışma mekanizmalarını inceleyen derin teknik araştırma raporudur.
🔬 1. WebRTC Protokol Sızıntısı ile Ağ Katmanı İzolasyon Bypass Analizi

Saldırganlar, ağ katmanında kimliklerini gizlemek adına askeri düzeyde şifrelenmiş VPN (Virtual Private Network) veya Tor düğümleri (Nodes) kullansalar dahi, uygulama katmanındaki tarayıcı motorları multimedya akışlarını optimize etmek adına yerel ağ bilgilerini dışarı sızdırabilir.
📡 ICE (Interactive Connectivity Establishment) ve SDP Ayrıştırma Mimarisi

WebRTC (Web Real-Time Communication) mimarisi, iki tarayıcının birbirine doğrudan (Peer-to-Peer) veri aktarabilmesi için STUN (Session Traversal Utilities for NAT) sunucularına binding istekleri gönderir.

    Host Adayları (Host Candidates): Tarayıcı, işletim sisteminin ağ arayüzlerini (getifaddrs()) sorgulayarak doğrudan cihaza bağlı olan yerel IP adreslerini (192.168.1.X, 10.0.0.X) toplar.

    Kapsülleme Hatası (TUN/TAP Bypass): Birçok ticari VPN yazılımı sadece işletim sisteminin routing tablosunu (Gateway) manipüle eder; fakat tarayıcı çekirdeğindeki (Chromium V8 veya Gecko) WebRTC modülü, doğrudan ham soketler üzerinden tüm yerel arayüzleri tek tek enumerate ettiği için VPN tünelini (TUN/TAP interface) bypass ederek ham yerel IP verisini yakalar.

💻 Adli Bilişim Veri Toplama Çekirdeği (telemetry.js)

Sistemimizin arka planında çalışan ve saldırganın SDP (Session Description Protocol) çıktısından ham IP adres yapısını cımbızlayan asenkron JavaScript telemetri mimarisi:
JavaScript

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

🧬 2. Canvas ve WebGL Donanımsal Parmak İzi (Hardware Fingerprinting) ve Matematiksel Entropi Hesaplaması

Siber suçlular IP adreslerini sürekli değiştirseler, tarayıcı çerezlerini (cookies) temizleseler veya "Gizli Sekme" (Incognito Mode) kullansalar dahi, kullandıkları bilgisayarın donanımsal mikro-mimarisini değiştiremezler.
🎨 OS Font Rasterization ve GPU Render Farklılıkları

Canvas parmak izi, tarayıcının HTML5 <canvas> elementi üzerinde görünmez bir 3D/2D grafik ve spesifik yazı tipleri (fonts) işlemesi esasına dayanır.

    İşletim Sistemi Entropisi: Windows (DirectWrite), macOS (CoreText) ve Linux (FreeType) yazı tiplerini ekrana basarken farklı pikselsel yumuşatma (anti-aliasing) algoritmaları kullanır.

    GPU (Ekran Kartı) Mikro-Mimarisi: Ekran kartının (NVIDIA, AMD, Intel) render motoru, pikselleri sıkıştırırken ve renk geçişlerini (gradient) hesaplarken donanım seviyesinde milisaniyelik ve mikron düzeyde farklılıklar üretir.

Üretilen bu ham piksel haritasının (Base64) benzersizlik derecesi (Şeffaf Bilgi Entropisi - Shannon Entropy), sisteme giren binlerce tehdit aktörü arasından tam isabet ayırt etme yeteneğini belirler ve şu matematiksel formülle hesaplanır:
H(X)=−i=1∑n​P(xi​)log2​P(xi​)
💻 WebGL Ekran Kartı Kimlik Deşifre Motoru

Sistem, sadece Canvas değil, WebGL katmanına sızarak ekran kartının ham donanımsal marka ve model ismini (UNMASKED_RENDERER_WEBGL) doğrudan sızdırır:
JavaScript

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

🗺️ 3. MITRE ATT&CK® Deception (Aldatıcı Savunma) ve Cyber Kill Chain Matrisi Entegrasyonu

Canary-Web platformu, saldırganların sızma operasyonlarındaki davranışsal reflekslerini (TTP - Tactics, Techniques, and Procedures) manipüle etmek üzere tasarlanmıştır. Geliştirilen bal küpü ve yem yapıları MITRE ATT&CK Matrix üzerinde doğrudan şu taktiklerle eşleşmektedir:
MITRE ATT&CK Taktik / Teknik Kodu	Teknik Adı	Canary-Web Karşılığı ve Operasyonel Mantığı
TA0007 // T1083	Discovery // File and Directory Discovery	Saldırganın sunucu içerisindeki dizinleri deşifre etmeye çalışırken /templates veya root dizindeki kritik dosyaları araması.
TA0006 // T1552.001	Credential Access // Credentials in Files	Kök dizine yerleştirilen admin_sifreler.txt dosyasının web/SSH tabanlı bir taramayla sızdırılması aşaması.
TA0008 // T1071.001	Command and Control // Web Protocols	Saldırganın gizli yolları tararken /t/<uuid> biçimindeki Honeytoken (Yem Linki) rotasına istek göndermesi.
Mitigation // M1050	Deception Deployment	Saldırgana sahte sistem kimlikleri ve zehirlenmiş payloadlar beslenerek gerçek sistem kaynaklarından izole edilmesi.
📡 4. Siber Tehdit İstihbaratı (CTI) ve STIX v2.1 Yapısal Log Entegrasyonu

Canary-Web adli bilişim motoru, topladığı tarayıcı telemetrilerini standart log mekanizmaları gibi düz metin olarak saklamaz. Elde edilen tüm dijital kanıtlar, uluslararası siber savunma standardı olan STIX v2.1 (Structured Threat Information Expression) JSON formatında paketlenir. Bu sayede üretilen istihbarat, kurumsal SIEM (Splunk, QRadar) veya SOAR sistemlerine doğrudan beslenebilir.
📄 Gerçek Zamanlı Üretilen Kurumsal İstihbarat Paketi (STIX Payload)
JSON

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

🧪 5. Active Tarpitting (Oyalama Tuzağı) ve TCP/HTTP Katmanında Kaynak Tüketimi

Sistemimize entegre edilen derin bir diğer savunma mekanizması Active Tarpitting (Zift Tuzağı) algoritmasıdır. Saldırganın bir insan değil, otomatize bir Python scripti (requests veya urllib) veya siber tarama aracı (Dirbuster, Nikto) olduğu tespit edildiğinde, backend kural motoru HTTP yanıt başlıklarını (Headers) kasıtlı olarak asenkron bir biçimde geciktirerek gönderir.

    TCP Pencere Manipülasyonu: Yanıtın her bir karakteri arasına time.sleep(0.5) gibi süreler koyularak bağlantı hattı açık tutulur.

    Tehdit Aktörünün Felç Edilmesi: Saldırgan bot yazılım, sunucudan yanıt alana kadar kilitlenir (blocking mod). Bu durum, saldırganın kendi CPU ve RAM kaynaklarını sömürerek kurumsal ağdaki diğer gerçek sunucuları taramasını fiziksel olarak engeller.