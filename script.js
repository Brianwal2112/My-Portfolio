// Theme management
const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'light-mode') {
    document.body.classList.add('light-mode');
    document.querySelector('.toggle-icon').textContent = '??';
}

function toggleTheme() {
    const body = document.body;
    const toggleIcon = document.querySelector('.toggle-icon');

    if (body.classList.contains('light-mode')) {
        body.classList.remove('light-mode');
        localStorage.setItem('theme', 'dark-mode');
        toggleIcon.textContent = '??';
    } else {
        body.classList.add('light-mode');
        localStorage.setItem('theme', 'light-mode');
        toggleIcon.textContent = '??';
    }
}

document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

// Navigation active state
function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-menu a');

    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setActiveNavLink();

    // Form submission handler
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = this.querySelector('input[name="name"]')?.value.trim();
            const email = this.querySelector('input[name="email"]')?.value.trim();
            const message = this.querySelector('textarea[name="message"]')?.value.trim();

            if (!name || !email || !message) {
                alert('Please fill in all required fields.');
                return;
            }

            const subject = encodeURIComponent('Contact Form Message from ' + name);
            const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`);
            window.location.href = `mailto:ochemehenry24@gmail.com?subject=${subject}&body=${body}`;
            
            this.reset();
            alert('Thank you! Your email client has been opened.');
        });
    }
});
