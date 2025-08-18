// Animation de chargement
document.addEventListener('DOMContentLoaded', () => {
    // Effet de transition entre les pages
    document.body.style.opacity = '1';
    
    // Validation des formulaires
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Chargement...';
            
            // Simuler un délai pour l'animation
            await new Promise(resolve => setTimeout(resolve, 1000));
        });
    });
});