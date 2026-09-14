// ========================
// WealthWise Investment Website JavaScript
// ========================

// Auth Modal Logic
const authModal = document.getElementById('authModal');
const closeModal = document.getElementById('closeModal');
const signupForm = document.getElementById('signupForm');
const loginForm = document.getElementById('loginForm');

function openAuthModal(mode = 'signup') {
    authModal.style.display = 'flex';
    switchAuthMode(mode);
}

function closeAuthModal() {
    authModal.style.display = 'none';
}

function switchAuthMode(mode) {
    if (mode === 'signup') {
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
    } else {
        signupForm.style.display = 'none';
        loginForm.style.display = 'block';
    }
}

function handleAuthSubmit(event, type) {
    event.preventDefault();
    // Simulate authentication
    alert(`${type === 'signup' ? 'Account created!' : 'Logged in successfully!'} Redirecting to dashboard...`);
    window.location.href = 'dashboard.html';
}

closeModal?.addEventListener('click', closeAuthModal);
window.addEventListener('click', (e) => {
    if (e.target === authModal) closeAuthModal();
});

// Mobile Navigation Toggle
const mobileToggle = document.getElementById('mobileToggle');
const navMenu = document.getElementById('navMenu');

mobileToggle?.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    const icon = mobileToggle.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-times');
});

// Close mobile menu when clicking on a nav link
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.add('fa-bars');
        icon.classList.remove('fa-times');
    });
});

// Update "Get Started" button in navbar to open modal
const getStartedBtn = document.querySelector('.nav-link.btn-primary');
getStartedBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    openAuthModal('signup');
});

// Navbar background on scroll
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
        navbar.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
});

// Investment Calculator
function calculateInvestment() {
    const initialInvestment = parseFloat(document.getElementById('initialInvestment').value) || 0;
    const monthlyContribution = parseFloat(document.getElementById('monthlyContribution').value) || 0;
    const returnRate = parseFloat(document.getElementById('returnRate').value) || 0;
    const timePeriod = parseFloat(document.getElementById('timePeriod').value) || 0;

    const monthlyRate = returnRate / 100 / 12;
    const totalMonths = timePeriod * 12;

    // Future value calculation with compound interest
    const futureValueInitial = initialInvestment * Math.pow(1 + monthlyRate, totalMonths);

    let futureValueContributions = 0;
    if (monthlyRate > 0) {
        futureValueContributions = monthlyContribution *
            ((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate);
    } else {
        futureValueContributions = monthlyContribution * totalMonths;
    }

    const finalBalance = futureValueInitial + futureValueContributions;
    const totalInvested = initialInvestment + (monthlyContribution * totalMonths);
    const interestEarned = finalBalance - totalInvested;

    // Animate the results
    animateValue('totalInvestment', totalInvested);
    animateValue('interestEarned', interestEarned);
    animateValue('finalBalance', finalBalance);
}

// Number animation function
function animateValue(elementId, value) {
    const element = document.getElementById(elementId);
    const start = 0;
    const end = value;
    const duration = 800;
    const startTime = performance.now();

    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (end - start) * easeOutQuart;

        element.textContent = formatCurrency(current);

        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }

    requestAnimationFrame(updateValue);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Live market data simulation (updates every 5 seconds)
function simulateMarketData() {
    const markets = [
        { id: 'spx', basePrice: 4783.45, volatility: 0.002 },
        { id: 'ixic', basePrice: 15056.92, volatility: 0.003 },
        { id: 'dji', basePrice: 37545.33, volatility: 0.0015 },
        { id: 'btc', basePrice: 43892.15, volatility: 0.01 }
    ];

    const marketCards = document.querySelectorAll('.market-card');

    marketCards.forEach((card, index) => {
        const market = markets[index];
        if (!market) return;

        const priceEl = card.querySelector('.price');
        const changeEl = card.querySelector('.change');
        const chartSvg = card.querySelector('.mini-chart svg path');

        // Simulate price change
        const change = (Math.random() - 0.5) * 2 * market.volatility;
        const newPrice = market.basePrice * (1 + change);
        const changePercent = change * 100;

        // Update price display
        priceEl.textContent = formatMarketPrice(newPrice, market.id === 'btc');

        // Update change indicator
        const isPositive = changePercent >= 0;
        changeEl.className = `change ${isPositive ? 'positive' : 'negative'}`;
        changeEl.innerHTML = `
            ${isPositive ? '+' : ''}${changePercent.toFixed(2)}%
            <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i>
        `;

        // Update mini chart color
        if (chartSvg) {
            chartSvg.setAttribute('stroke', isPositive ? '#10b981' : '#ef4444');
        }
    });
}

function formatMarketPrice(price, isCrypto) {
    if (isCrypto) {
        return '$' + price.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    return price.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Initialize market data updates
setInterval(simulateMarketData, 5000);

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80; // Account for fixed navbar
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-visible');
            fadeInObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Add fade-in animation to elements
document.querySelectorAll('.feature-card, .market-card, .testimonial-card, .pricing-card').forEach(el => {
    el.classList.add('fade-in');
    fadeInObserver.observe(el);
});

// Add CSS for fade-in animation
const style = document.createElement('style');
style.textContent = `
    .fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .fade-in-visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Stagger animations */
    .feature-card:nth-child(1) { transition-delay: 0s; }
    .feature-card:nth-child(2) { transition-delay: 0.1s; }
    .feature-card:nth-child(3) { transition-delay: 0.2s; }
    .feature-card:nth-child(4) { transition-delay: 0.3s; }
    .feature-card:nth-child(5) { transition-delay: 0.4s; }
    .feature-card:nth-child(6) { transition-delay: 0.5s; }

    .market-card:nth-child(1) { transition-delay: 0s; }
    .market-card:nth-child(2) { transition-delay: 0.1s; }
    .market-card:nth-child(3) { transition-delay: 0.2s; }
    .market-card:nth-child(4) { transition-delay: 0.3s; }

    .pricing-card:nth-child(1) { transition-delay: 0s; }
    .pricing-card:nth-child(2) { transition-delay: 0.1s; }
    .pricing-card:nth-child(3) { transition-delay: 0.2s; }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initial calculation
    calculateInvestment();

    // Add event listeners to calculator inputs
    ['initialInvestment', 'monthlyContribution', 'returnRate', 'timePeriod'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', calculateInvestment);
        }
    });

    // Add hover effect for feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
});

// Add keyboard navigation support
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        navMenu.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.add('fa-bars');
        icon.classList.remove('fa-times');
        closeAuthModal();
    }
});

// Touch swipe support for mobile menu
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeThreshold = 100;
    const diff = touchStartX - touchEndX;

    // Swipe left to close menu
    if (diff > swipeThreshold && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.add('fa-bars');
        icon.classList.remove('fa-times');
    }

    // Swipe right to open menu (only from left edge)
    if (diff < -swipeThreshold && touchStartX < 50) {
        navMenu.classList.add('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-times');
    }
}
 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
        navbar.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
});

// Investment Calculator
function calculateInvestment() {
    const initialInvestment = parseFloat(document.getElementById('initialInvestment').value) || 0;
    const monthlyContribution = parseFloat(document.getElementById('monthlyContribution').value) || 0;
    const returnRate = parseFloat(document.getElementById('returnRate').value) || 0;
    const timePeriod = parseFloat(document.getElementById('timePeriod').value) || 0;

    const monthlyRate = returnRate / 100 / 12;
    const totalMonths = timePeriod * 12;

    // Future value calculation with compound interest
    const futureValueInitial = initialInvestment * Math.pow(1 + monthlyRate, totalMonths);

    let futureValueContributions = 0;
    if (monthlyRate > 0) {
        futureValueContributions = monthlyContribution *
            ((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate);
    } else {
        futureValueContributions = monthlyContribution * totalMonths;
    }

    const finalBalance = futureValueInitial + futureValueContributions;
    const totalInvested = initialInvestment + (monthlyContribution * totalMonths);
    const interestEarned = finalBalance - totalInvested;

    // Animate the results
    animateValue('totalInvestment', totalInvested);
    animateValue('interestEarned', interestEarned);
    animateValue('finalBalance', finalBalance);
}

// Number animation function
function animateValue(elementId, value) {
    const element = document.getElementById(elementId);
    const start = 0;
    const end = value;
    const duration = 800;
    const startTime = performance.now();

    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (end - start) * easeOutQuart;

        element.textContent = formatCurrency(current);

        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }

    requestAnimationFrame(updateValue);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Live market data simulation (updates every 5 seconds)
function simulateMarketData() {
    const markets = [
        { id: 'spx', basePrice: 4783.45, volatility: 0.002 },
        { id: 'ixic', basePrice: 15056.92, volatility: 0.003 },
        { id: 'dji', basePrice: 37545.33, volatility: 0.0015 },
        { id: 'btc', basePrice: 43892.15, volatility: 0.01 }
    ];

    const marketCards = document.querySelectorAll('.market-card');

    marketCards.forEach((card, index) => {
        const market = markets[index];
        if (!market) return;

        const priceEl = card.querySelector('.price');
        const changeEl = card.querySelector('.change');
        const chartSvg = card.querySelector('.mini-chart svg path');

        // Simulate price change
        const change = (Math.random() - 0.5) * 2 * market.volatility;
        const newPrice = market.basePrice * (1 + change);
        const changePercent = change * 100;

        // Update price display
        priceEl.textContent = formatMarketPrice(newPrice, market.id === 'btc');

        // Update change indicator
        const isPositive = changePercent >= 0;
        changeEl.className = `change ${isPositive ? 'positive' : 'negative'}`;
        changeEl.innerHTML = `
            ${isPositive ? '+' : ''}${changePercent.toFixed(2)}%
            <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i>
        `;

        // Update mini chart color
        if (chartSvg) {
            chartSvg.setAttribute('stroke', isPositive ? '#10b981' : '#ef4444');
        }
    });
}

function formatMarketPrice(price, isCrypto) {
    if (isCrypto) {
        return '$' + price.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    return price.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Initialize market data updates
setInterval(simulateMarketData, 5000);

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80; // Account for fixed navbar
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-visible');
            fadeInObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Add fade-in animation to elements
document.querySelectorAll('.feature-card, .market-card, .testimonial-card').forEach(el => {
    el.classList.add('fade-in');
    fadeInObserver.observe(el);
});

// Add CSS for fade-in animation
const style = document.createElement('style');
style.textContent = `
    .fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .fade-in-visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Stagger animations */
    .feature-card:nth-child(1) { transition-delay: 0s; }
    .feature-card:nth-child(2) { transition-delay: 0.1s; }
    .feature-card:nth-child(3) { transition-delay: 0.2s; }
    .feature-card:nth-child(4) { transition-delay: 0.3s; }
    .feature-card:nth-child(5) { transition-delay: 0.4s; }
    .feature-card:nth-child(6) { transition-delay: 0.5s; }

    .market-card:nth-child(1) { transition-delay: 0s; }
    .market-card:nth-child(2) { transition-delay: 0.1s; }
    .market-card:nth-child(3) { transition-delay: 0.2s; }
    .market-card:nth-child(4) { transition-delay: 0.3s; }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initial calculation
    calculateInvestment();

    // Add event listeners to calculator inputs
    ['initialInvestment', 'monthlyContribution', 'returnRate', 'timePeriod'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', calculateInvestment);
        }
    });

    // Add hover effect for feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
});

// Add keyboard navigation support
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        navMenu.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.add('fa-bars');
        icon.classList.remove('fa-times');
    }
});

// Touch swipe support for mobile menu
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeThreshold = 100;
    const diff = touchStartX - touchEndX;

    // Swipe left to close menu
    if (diff > swipeThreshold && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.add('fa-bars');
        icon.classList.remove('fa-times');
    }

    // Swipe right to open menu (only from left edge)
    if (diff < -swipeThreshold && touchStartX < 50) {
        navMenu.classList.add('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-times');
    }
}
