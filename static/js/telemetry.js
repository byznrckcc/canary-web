/* static/js/telemetry.js - Real-Time DOM Event Binder & Forensic Decoder */
document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.attacker-row');
    
    rows.forEach(function(row) {
        row.addEventListener('click', function() {
            // 1. Tırnak işaretlerine takılmadan aktif savunma kodlarını panellere aktarır
            document.getElementById('ipTablesZone').value = this.getAttribute('data-iptables');
            document.getElementById('snortZone').value = this.getAttribute('data-snort');
            document.getElementById('pfZone').value = this.getAttribute('data-pfsense'); // Eksik olan pfSense API hattı eklendi
            document.getElementById('riskMeter').innerText = '%' + this.getAttribute('data-risk');
            
            // 2. Base64 maskeli uluslararası STIX siber istihbarat payload'unu deşifre eder
            try {
                let b64Data = this.getAttribute('data-stix');
                if (b64Data) {
                    let decodedStix = atob(b64Data);
                    // Deşifre edilen JSON verisini okunaklı biçimde (Pretty Print) ekrana basar
                    document.getElementById('stixZone').value = JSON.stringify(JSON.parse(decodedStix), null, 2);
                }
            } catch(e) {
                document.getElementById('stixZone').value = "[-] CTI Cyber Threat Payload Parsing Error: Integrity Violated.";
            }
            
            // 3. Seçilen satıra elit mor neon odaklanma efekti uygular
            rows.forEach(r => r.style.backgroundColor = 'transparent');
            this.style.backgroundColor = 'rgba(99, 102, 241, 0.25)';
            
            // Konsola Mr. Robot tarzı adli takip logu fırlatır (F12 inceleme alanı için)
            console.log("[+] Forensic Target Selected. De-anonymization matrix extracted successfully.");
        });
    });

    // Canlı Sistem Log İşleme Akışı Simülasyonu
    const termBox = document.getElementById('termStream');
    if (termBox) {
        const sysLogs = [
            "INFO  :: Asynchronous logging worker thread started.",
            "SUCCESS :: Anti-Fingerprinting cipher suite active.",
            "INFO  :: Active tarpitting matrix listening on /t/<uuid>",
            "READY :: OWASP secure HTTP headers validator initialized.",
            "DECRYPT :: WebRTC De-anonymization module hook attached."
        ];
        sysLogs.forEach((log, idx) => {
            setTimeout(() => {
                termBox.innerHTML += `<div>[${new Date().toISOString().slice(11,19)}] ${log}</div>`;
                termBox.scrollTop = termBox.scrollHeight;
            }, idx * 400);
        });
    }
});

// Jüri önünde tek tıkla simülasyon alarmı üreten asenkron fonksiyon
function triggerSimulation() {
    fetch('/api/v1/tokens/generate', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        fetch(data.trigger_url).then(() => {
            window.location.reload();
        });
    });
}