document.addEventListener('DOMContentLoaded', function() {
    const tooltip = document.getElementById('tooltip');
    const markers = document.querySelectorAll('.evento-marker');
    
    markers.forEach(marker => {
        marker.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.left = `${rect.left + window.scrollX}px`;
            tooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
            tooltip.style.opacity = '1';
        });
        
        marker.addEventListener('mouseleave', function() {
            tooltip.style.opacity = '0';
        });
    });
});