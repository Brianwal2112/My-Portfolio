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

// Form submission handler with credential saving
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

            // Save credentials to localStorage
            if(name && email) {
                const credentials = {
                    name: name,
                    email: email,
                    timestamp: new Date().toISOString()
                };

                localStorage.setItem('portfolioCredentials', JSON.stringify(credentials));
                console.log('Credentials saved:', credentials);
            }

            // In a real application, you would handle form submission here
            alert('Thank you for your message! This is a demo, so no actual submission occurs.\n\nCredentials have been saved to browser storage.');

            // Reset form
            this.reset();

            // Pre-fill form with saved credentials if available
            loadSavedCredentials();
        });
    }

    // Load saved credentials when page loads
    loadSavedCredentials();

    // Set active navigation link
    setActiveNavLink();
    
    // Initialize cursor follower if element exists
    initCursorFollower();
    
    // Initialize project card enhancements
    initProjectCardEnhancements();
});

// Load saved credentials from localStorage if available
function loadSavedCredentials() {
    const savedCredentials = localStorage.getItem('portfolioCredentials');
    if(savedCredentials) {
        try {
            const credentials = JSON.parse(savedCredentials);
            const nameInput = document.querySelector('#name') || document.querySelector('.contact-form input[type="text"]');
            const emailInput = document.querySelector('#email') || document.querySelector('.contact-form input[type="email"]');

            if(nameInput && credentials.name) {
                nameInput.value = credentials.name;
            }

            if(emailInput && credentials.email) {
                emailInput.value = credentials.email;
            }
        } catch(e) {
            console.error('Error loading saved credentials:', e);
        }
    }
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

// Add humorous mouse-avoiding behavior to buttons on homepage
function initButtonAvoidance() {
    // Only apply to homepage buttons
    if (window.location.pathname.includes('index.html') || window.location.pathname === '' || window.location.pathname.includes('home')) {
        const buttons = document.querySelectorAll('.btn, .project-link, .project-external-link, .theme-toggle-btn, button');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', (e) => {
                // Calculate random direction to move away
                const angle = Math.random() * Math.PI * 2; // Random angle in radians
                const distance = 20 + Math.random() * 30; // Random distance between 20-50px
                const moveX = Math.cos(angle) * distance;
                const moveY = Math.sin(angle) * distance;
                
                // Apply the transformation
                button.style.transition = 'transform 0.3s ease';
                button.style.transform = `translate(${moveX}px, ${moveY}px)`;
                
                // Reset position after 7 seconds
                setTimeout(() => {
                    button.style.transform = 'translate(0, 0)';
                }, 7000);
            });
        });
    }
}

// Enhance project cards with technology tags
function initProjectCardEnhancements() {
    const projectCards = document.querySelectorAll('.project-card');
    
    projectCards.forEach(card => {
        // Find the technologies paragraph
        const techParagraph = card.querySelector('p strong:nth-of-type(2)').closest('p');
        if (techParagraph) {
            const technologiesText = techParagraph.textContent.replace('Technologies: ', '');
            const technologies = technologiesText.split(', ');
            
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
    
    // Initialize button avoidance on homepage
    initButtonAvoidance();
});