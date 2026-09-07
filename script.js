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
            finalizeLoad();
        }
        if(percentText) percentText.textContent = count + '%';
        if(progressBar) progressBar.style.width = count + '%';
    }, 80);

    function finalizeLoad() {
        body.classList.remove('loading');
    }

    // --- CURSOR LOGIC ---
    const cursor = document.querySelector('.cursor');
    const follower = document.querySelector('.cursor-follower');
    let mouseX = 0, mouseY = 0, followerX = 0, followerY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if(cursor) {
            cursor.style.left = mouseX + 'px';
            cursor.style.top = mouseY + 'px';
        }
        
        // --- COLOR ADAPTATION LOGIC ---
        // Check element under cursor
        const element = document.elementFromPoint(mouseX, mouseY);
        if (element) {
            const bgColor = window.getComputedStyle(element).backgroundColor;
            // Convert rgb to grayscale value
            const rgb = bgColor.match(/\d+/g);
            if (rgb) {
                const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
                if (brightness < 128) {
                    cursor?.classList.add('cursor-inverted');
                    follower?.classList.add('cursor-inverted');
                } else {
                    cursor?.classList.remove('cursor-inverted');
                    follower?.classList.remove('cursor-inverted');
                }
            }
        }
    });

    function animateCursor() {
        followerX += (mouseX - followerX) * 0.1;
        followerY += (mouseY - followerY) * 0.1;
        if(follower) {
            follower.style.left = followerX + 'px';
            follower.style.top = followerY + 'px';
        }
        requestAnimationFrame(animateCursor);
    }
    animateCursor();

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

    if(menuTrigger && menuOverlay) {
        menuTrigger.addEventListener('click', () => {
            menuTrigger.classList.toggle('active');
            menuOverlay.classList.toggle('active');
            if(menuOverlay.classList.contains('active')) {
                menuItems.forEach((item, index) => {
                    item.style.setProperty('--i', index);
                });
            }
        });

        menuItems.forEach(link => {
            link.addEventListener('click', () => {
                menuTrigger.classList.remove('active');
                menuOverlay.classList.remove('active');
            });
        });
    }

    // --- REVEAL ANIMATIONS ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, { threshold: 0.15 });

    document.querySelectorAll('.reveal, .reveal-delayed').forEach(el => observer.observe(el));

    // --- CONTACT FORM AJAX ---
    const contactForm = document.getElementById('contactForm');
    if(contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(contactForm);
            const submitBtn = contactForm.querySelector('button');
            const originalBtnText = submitBtn.textContent;
            
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;

            try {
                const response = await fetch(contactForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'Accept-Name': 'application/json' }
                });

                if (response.ok) {
                    submitBtn.textContent = 'Message Sent!';
                    contactForm.reset();
                } else {
                    submitBtn.textContent = 'Error occurred';
                }
            } catch (err) {
                submitBtn.textContent = 'Error occurred';
            } finally {
                setTimeout(() => {
                    submitBtn.textContent = originalBtnText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    }
});
