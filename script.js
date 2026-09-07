document.addEventListener('DOMContentLoaded', () => {
    // --- PRELOADER LOGIC ---
    const body = document.body;
    const percentText = document.querySelector('.loader-percent');
    const progressBar = document.querySelector('.progress');
    
    let count = 0;
    const loadInterval = setInterval(() => {
        count += Math.floor(Math.random() * 10) + 1;
        if (count >= 100) {
            count = 100;
            clearInterval(loadInterval);
            setTimeout(() => {
                body.classList.remove('loading');
            }, 500);
        }
        percentText.textContent = count + '%';
        progressBar.style.width = count + '%';
    }, 80);

    // --- CURSOR LOGIC ---
    const cursor = document.querySelector('.cursor');
    const follower = document.querySelector('.cursor-follower');
    let mouseX = 0, mouseY = 0, followerX = 0, followerY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursor.style.left = mouseX + 'px';
        cursor.style.top = mouseY + 'px';
    });

    function animateCursor() {
        followerX += (mouseX - followerX) * 0.1;
        followerY += (mouseY - followerY) * 0.1;
        follower.style.left = followerX + 'px';
        follower.style.top = followerY + 'px';
        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // --- BLOB MOVEMENT ---
    const blobs = document.querySelectorAll('.blob');
    document.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth) - 0.5;
        const y = (e.clientY / window.innerHeight) - 0.5;
        
        blobs.forEach((blob, i) => {
            const shift = (i + 1) * 20;
            blob.style.transform = `translate(${x * shift}px, ${y * shift}px)`;
        });
    });

    // --- MAGNETIC EFFECT ---
    const magnetics = document.querySelectorAll('.magnetic');
    magnetics.forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            el.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
        });
        el.addEventListener('mouseleave', () => {
            el.style.transform = `translate(0, 0)`;
        });
    });

    // --- MENU LOGIC ---
    const menuTrigger = document.getElementById('menuTrigger');
    const menuOverlay = document.querySelector('.menu-overlay');
    const menuItems = document.querySelectorAll('.menu-item a');

    menuTrigger.addEventListener('click', () => {
        menuTrigger.classList.toggle('active');
        menuOverlay.classList.toggle('active');
        if(menuOverlay.classList.contains('active')) {
            menuItems.forEach((item, index) => {
                item.style.setProperty('--i', index);
            });
        }
    });

    // --- REVEAL ANIMATIONS ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.reveal, .reveal-delayed').forEach(el => observer.observe(el));
});
