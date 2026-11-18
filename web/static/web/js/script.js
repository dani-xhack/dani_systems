document.addEventListener("DOMContentLoaded", function() {
    // 1. Плавное появление секций при прокрутке
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    const sections = document.querySelectorAll('section, main');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'all 0.8s ease-out';
        observer.observe(section);
    });

    // 2. Параллакс для слоя с точками
    const bgDots = document.querySelector('.bg-dots');
    if (bgDots) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            bgDots.style.backgroundPositionY = `${scrolled * 0.4}px`; 
        });
    }
});
