// Mobile menu toggle functionality
function initializeMobileMenu() {
    const nav = document.getElementById('nav-menu');
    const menuToggle = document.getElementById('menu-toggle');

    if (!nav || !menuToggle || menuToggle.dataset.mobileMenuInitialized === 'true') {
        return;
    }

    menuToggle.dataset.mobileMenuInitialized = 'true';

    document.addEventListener('click', function (event) {
        if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
            nav.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
        }
    });

    nav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function () {
            nav.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMobileMenu);
} else {
    initializeMobileMenu();
}