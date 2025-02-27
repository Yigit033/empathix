// Empathix JavaScript Dosyası

// Metin alanını temizleme fonksiyonu
function clearText() {
    document.getElementById('text').value = '';
}

// Sayfa yüklendiğinde çalışacak kod
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltip'leri etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Analiz sonuçlarını göster/gizle toggle
    const toggleButtons = document.querySelectorAll('.toggle-details');
    if (toggleButtons) {
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const targetElement = document.getElementById(targetId);
                
                if (targetElement.style.display === 'none' || !targetElement.style.display) {
                    targetElement.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-chevron-up"></i> Detayları Gizle';
                } else {
                    targetElement.style.display = 'none';
                    this.innerHTML = '<i class="fas fa-chevron-down"></i> Detayları Göster';
                }
            });
        });
    }
    
    // Analiz formu gönderildiğinde yükleme animasyonu göster
    const analysisForm = document.querySelector('form[action="/analyze"]');
    if (analysisForm) {
        analysisForm.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analiz Ediliyor...';
                submitButton.disabled = true;
            }
        });
    }
});
