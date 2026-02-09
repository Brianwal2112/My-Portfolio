// Check for saved theme preference in localStorage
const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'light-mode') {
    document.body.classList.add('light-mode');
    document.querySelector('.toggle-icon').textContent = '☀️';
}

// Toggle theme function
function toggleTheme() {
    const body = document.body;
    const toggleIcon = document.querySelector('.toggle-icon');

    if (body.classList.contains('light-mode')) {
        // Switch to dark mode
        body.classList.remove('light-mode');
        localStorage.setItem('theme', 'dark-mode');
        toggleIcon.textContent = '🌙';
    } else {
        // Switch to light mode
        body.classList.add('light-mode');
        localStorage.setItem('theme', 'light-mode');
        toggleIcon.textContent = '☀️';
    }
}

// Add event listener to the theme toggle button
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

// Set active navigation link based on current page
function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-menu a');

    navLinks.forEach(link => {
        link.classList.remove('active');
        // Compare the href with current page
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

// Add smooth scrolling for navigation links (only on index.html)
if (window.location.pathname.includes('index.html') || window.location.pathname === '') {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Form submission handler - Professional version without credential storage
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Get form values
            const nameInput = this.querySelector('#name') || this.querySelector('input[type="text"]');
            const emailInput = this.querySelector('#email') || this.querySelector('input[type="email"]');
            const messageTextarea = this.querySelector('#message') || this.querySelector('textarea');

            const name = nameInput ? nameInput.value.trim() : '';
            const email = emailInput ? emailInput.value.trim() : '';
            const message = messageTextarea ? messageTextarea.value.trim() : '';

            // Form validation
            if (!name || !email || !message) {
                showFormNotification('Please fill in all required fields.', 'error');
                return;
            }

            // Create mailto link for form submission
            const subject = encodeURIComponent('Contact Form Message from ' + name);
            const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`);
            const mailtoLink = `mailto:ochemehenry24@gmail.com?subject=${subject}&body=${body}`;

            // Open email client
            window.location.href = mailtoLink;

            // Show success message
            showFormNotification('Thank you for your message! Your email client should open with the details.', 'success');

            // Reset form
            this.reset();
        });
    }

    // Set active navigation link
    setActiveNavLink();

    // Initialize cursor follower if element exists
    initCursorFollower();

    // Initialize project card enhancements
    initProjectCardEnhancements();
});

// Show form notification
function showFormNotification(message, type = 'success') {
    // Remove existing notifications
    const existing = document.querySelector('.form-notification');
    if (existing) existing.remove();

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `form-notification ${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${type === 'success' ? '✓' : '✗'}</span>
        <span>${message}</span>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
        transform: translateX(120%);
        transition: transform 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.style.transform = 'translateX(0)', 10);

    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(120%)';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Mouse cursor follower functionality
function initCursorFollower() {
    const cursor = document.querySelector('.cursor-follower');
    if (!cursor) return;

    // Track mouse movement
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
    });

    // Add hover effects
    const hoverElements = document.querySelectorAll('a, button, .project-card, .theme-toggle-btn');
    hoverElements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            cursor.classList.add('hover');
        });

        element.addEventListener('mouseleave', () => {
            cursor.classList.remove('hover');
        });
    });
    
    // Create subtle cursor trail effect
    createCursorTrail();
}

// Create subtle cursor trail effect
function createCursorTrail() {
    const coords = { x: 0, y: 0 };
    const circles = [];
    const colors = [
        'rgba(187, 134, 252, 0.3)', // accent color
        'rgba(139, 195, 74, 0.3)',  // green
        'rgba(255, 152, 0, 0.3)',   // orange
        'rgba(33, 150, 243, 0.3)'   // blue
    ];

    // Create 10 trail elements
    for (let i = 0; i < 10; i++) {
        const circle = document.createElement('div');
        circle.classList.add('cursor-trail');
        circle.style.backgroundColor = colors[i % colors.length];
        document.body.appendChild(circle);
        circles.push(circle);
    }

    // Track mouse coordinates
    document.addEventListener('mousemove', (e) => {
        coords.x = e.clientX;
        coords.y = e.clientY;
    });

    // Animate the trail
    const animateCircles = () => {
        let x = coords.x;
        let y = coords.y;

        circles.forEach((circle, index) => {
            // Delay each circle's movement for trailing effect
            setTimeout(() => {
                circle.style.left = `${x}px`;
                circle.style.top = `${y}px`;
                
                // Reduce opacity over time for fade effect
                const currentOpacity = parseFloat(circle.style.opacity || 0.4);
                circle.style.opacity = Math.max(0, currentOpacity - 0.05);
                
                // Reset opacity when it gets low
                if (parseFloat(circle.style.opacity) <= 0.1) {
                    circle.style.opacity = '0.4';
                }
            }, 100 * index);
        });

        requestAnimationFrame(animateCircles);
    };

    animateCircles();
}

// Initialize smooth scroll animations for buttons
function initButtonAnimations() {
    const buttons = document.querySelectorAll('.btn, .project-link, .project-external-link');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-3px)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
        });
    });
}

// Enhance project cards with technology tags - safely handles missing elements
function initProjectCardEnhancements() {
    const projectCards = document.querySelectorAll('.project-card');

    projectCards.forEach(card => {
        try {
            // Find the technologies paragraph safely
            const techStrong = card.querySelector('p strong');
            if (!techStrong || !techStrong.textContent.includes('Technologies')) return;

            const techParagraph = techStrong.closest('p');
            if (!techParagraph) return;

            const technologiesText = techParagraph.textContent.replace('Technologies:', '').trim();
            if (!technologiesText) return;

            const technologies = technologiesText.split(',').filter(t => t.trim());
            if (technologies.length === 0) return;

            // Create a container for technology tags
            const techContainer = document.createElement('div');
            techContainer.className = 'tech-tags-container';

            technologies.forEach(tech => {
                const tag = document.createElement('span');
                tag.className = 'tech-tag';
                tag.textContent = tech.trim();
                techContainer.appendChild(tag);
            });

            // Insert the tech tags after the technologies paragraph
            techParagraph.parentNode.insertBefore(techContainer, techParagraph.nextSibling);

            // Hide the original technologies paragraph
            techParagraph.style.display = 'none';
        } catch (e) {
            // Silently skip cards that don't match the expected structure
            console.log('Skipping project card enhancement for one card');
        }
    });
}

// Initialize color transition functionality
function initColorTransitions() {
    // Add the color-transition class to the body to enable background animation
    document.body.classList.add('color-transition');
    
    // The red and black glow effect is now handled by CSS
    // No JavaScript needed for the project card glow
}

// Initialize color transitions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Other initialization code is already here
    // ...
    
    // Initialize color transitions
    initColorTransitions();
    
    // Initialize button animations
    initButtonAnimations();
});