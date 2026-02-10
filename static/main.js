// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    document.getElementById('menu-toggle').addEventListener('click', function () {
        const nav = document.getElementById('nav-menu');
        nav.classList.toggle('active');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function (event) {
        const nav = document.getElementById('nav-menu');
        const menuToggle = document.getElementById('menu-toggle');

        if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
            nav.classList.remove('active');
        }
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', function () {
            document.getElementById('nav-menu').classList.remove('active');
        });
    });
});