// Sample reservation data
let reservations = JSON.parse(localStorage.getItem('reservations')) || [
    {
        id: 1,
        date: '2026-06-15',
        time: '19:00',
        guests: 2,
        name: 'John Smith',
        email: 'john@example.com',
        phone: '(555) 123-4567',
        specialRequests: 'Window seat preferred',
        status: 'confirmed'
    },
    {
        id: 2,
        date: '2026-06-16',
        time: '20:00',
        guests: 4,
        name: 'Sarah Johnson',
        email: 'sarah@example.com',
        phone: '(555) 987-6543',
        specialRequests: 'Anniversary celebration',
        status: 'confirmed'
    }
];

// DOM Elements
const reservationForm = document.querySelector('.reservation-form');
const dateInput = document.getElementById('date');
const timeSelect = document.getElementById('time');
const categoryButtons = document.querySelectorAll('.category-btn');
const menuCategories = document.querySelectorAll('.menu-category');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    // Set minimum date to today
    if(dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        dateInput.value = today;
    }
    
    // Add event listeners for reservation form
    if(reservationForm) {
        reservationForm.addEventListener('submit', makeReservation);
    }
    
    // Add event listeners for menu categories
    if(categoryButtons && menuCategories) {
        categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                button.classList.add('active');
                
                // Hide all menu categories
                menuCategories.forEach(cat => cat.classList.remove('active'));
                
                // Show the selected category
                const categoryId = button.getAttribute('data-category');
                document.getElementById(categoryId).classList.add('active');
            });
        });
    }
    
    // Add event listener for contact form
    const contactForm = document.querySelector('.contact-form');
    if(contactForm) {
        contactForm.addEventListener('submit', submitContactForm);
    }
    
    // Add event listeners for calendar navigation
    document.getElementById('prev-week')?.addEventListener('click', () => navigateWeek(-1));
    document.getElementById('next-week')?.addEventListener('click', () => navigateWeek(1));
    
    // Initialize calendar
    updateCalendarDisplay();
});

// Make a reservation
function makeReservation(e) {
    e.preventDefault();
    
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const guests = document.getElementById('guests').value;
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const specialRequests = document.getElementById('special-requests').value;
    
    if(!date || !time || !name || !email || !phone) {
        showNotification('Please fill in all required fields');
        return;
    }
    
    const newReservation = {
        id: Date.now(),
        date,
        time,
        guests,
        name,
        email,
        phone,
        specialRequests,
        status: 'confirmed'
    };
    
    reservations.push(newReservation);
    localStorage.setItem('reservations', JSON.stringify(reservations));
    
    showNotification('Reservation confirmed! We look forward to serving you.');
    
    // Reset form
    reservationForm.reset();
    
    // Set date to today
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
});

// Submit contact form
function submitContactForm(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    
    if(!name || !email || !subject || !message) {
        showNotification('Please fill in all fields');
        return;
    }
    
    showNotification('Message sent successfully! We\'ll get back to you soon.');
    e.target.reset();
}

// Navigate calendar by week
function navigateWeek(direction) {
    const currentDate = new Date(document.getElementById('date').value);
    currentDate.setDate(currentDate.getDate() + (direction * 7));
    
    const newDate = currentDate.toISOString().split('T')[0];
    document.getElementById('date').value = newDate;
    
    // Update calendar display
    updateCalendarDisplay();
}

// Update calendar display
function updateCalendarDisplay() {
    const currentDate = new Date(document.getElementById('date').value);
    const startDate = new Date(currentDate);
    startDate.setDate(startDate.getDate() - startDate.getDay()); // Start from Sunday
    
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + 6); // End on Saturday
    
    document.getElementById('current-week').textContent = 
        `${formatDate(startDate)} - ${formatDate(endDate)}`;
}

// Format date as MM/DD/YYYY
function formatDate(date) {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month}/${day}/${year}`;
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#8b4513';
    notification.style.color = 'white';
    notification.style.padding = '15px';
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '1000';
    notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 3000);
}

// Update time slots based on selected date
if(dateInput) {
    dateInput.addEventListener('change', function() {
        // In a real app, this would fetch available times for the selected date
        // For this demo, we'll just show a notification
        showNotification(`Available times updated for ${this.value}`);
    });
}