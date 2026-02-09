// Sample fitness data
let fitnessData = JSON.parse(localStorage.getItem('fitnessData')) || {
    dailySteps: 8421,
    caloriesBurned: 425,
    activeMinutes: 45,
    waterIntake: 6,
    weight: 172,
    workouts: [
        {
            id: 1,
            name: "Upper Body Strength",
            date: "2026-06-15",
            duration: 42,
            calories: 320,
            exercises: 8
        },
        {
            id: 2,
            name: "HIIT Cardio",
            date: "2026-06-14",
            duration: 30,
            calories: 450,
            exercises: 10
        },
        {
            id: 3,
            name: "Yoga Flow",
            date: "2026-06-13",
            duration: 38,
            calories: 180,
            exercises: 12
        }
    ],
    meals: [
        {
            id: 1,
            name: "Oatmeal with berries",
            calories: 320,
            time: "breakfast",
            date: "2026-06-15"
        },
        {
            id: 2,
            name: "Black coffee",
            calories: 5,
            time: "breakfast",
            date: "2026-06-15"
        },
        {
            id: 3,
            name: "Grilled chicken salad",
            calories: 450,
            time: "lunch",
            date: "2026-06-15"
        }
    ]
};

// DOM Elements
const dailyStepsEl = document.getElementById('daily-steps');
const caloriesBurnedEl = document.getElementById('calories-burned');
const activeMinutesEl = document.getElementById('active-minutes');
const waterIntakeEl = document.getElementById('water-intake');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    updateDashboardStats();
    
    // Add event listeners for quick action buttons
    document.getElementById('start-workout')?.addEventListener('click', startWorkout);
    document.getElementById('log-meal')?.addEventListener('click', logMeal);
    document.getElementById('record-weight')?.addEventListener('click', recordWeight);
    document.getElementById('log-water')?.addEventListener('click', logWater);
    
    // Add event listeners for workout actions
    document.querySelectorAll('.workout-action').forEach(button => {
        button.addEventListener('click', () => {
            const workoutName = button.closest('.workout-plan').querySelector('h3').textContent;
            startWorkout(workoutName);
        });
    });
    
    // Add event listeners for nutrition logging
    document.getElementById('log-meal-btn')?.addEventListener('click', logMeal);
});

// Update dashboard statistics
function updateDashboardStats() {
    if(dailyStepsEl) dailyStepsEl.textContent = fitnessData.dailySteps.toLocaleString();
    if(caloriesBurnedEl) caloriesBurnedEl.textContent = fitnessData.caloriesBurned;
    if(activeMinutesEl) activeMinutesEl.textContent = fitnessData.activeMinutes;
    if(waterIntakeEl) waterIntakeEl.textContent = fitnessData.waterIntake;
}

// Start a workout
function startWorkout(workoutName = "Custom Workout") {
    showNotification(`Starting ${workoutName} workout!`);
    
    // In a real app, this would start a workout timer
    // For now, we'll just show a notification
}

// Log a meal
function logMeal() {
    const mealName = prompt("What did you eat?");
    if(mealName) {
        const calories = prompt("How many calories?");
        if(calories) {
            const newMeal = {
                id: Date.now(),
                name: mealName,
                calories: parseInt(calories),
                time: "snack", // Could be breakfast, lunch, dinner, snack
                date: new Date().toISOString().split('T')[0]
            };
            
            fitnessData.meals.push(newMeal);
            localStorage.setItem('fitnessData', JSON.stringify(fitnessData));
            
            showNotification(`${mealName} logged (${calories} calories)`);
        }
    }
}

// Record weight
function recordWeight() {
    const weight = prompt("Enter your current weight (lbs):");
    if(weight) {
        fitnessData.weight = parseFloat(weight);
        localStorage.setItem('fitnessData', JSON.stringify(fitnessData));
        showNotification(`Weight recorded: ${weight} lbs`);
    }
}

// Log water intake
function logWater() {
    fitnessData.waterIntake++;
    localStorage.setItem('fitnessData', JSON.stringify(fitnessData));
    updateDashboardStats();
    showNotification(`Water intake increased to ${fitnessData.waterIntake} glasses`);
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#2e7d32';
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

// Simulate updating stats periodically
setInterval(() => {
    // Simulate step count increasing throughout the day
    if(fitnessData.dailySteps < 10000) {
        fitnessData.dailySteps += Math.floor(Math.random() * 10);
        localStorage.setItem('fitnessData', JSON.stringify(fitnessData));
        updateDashboardStats();
    }
}, 30000); // Update every 30 seconds

// Initialize chart placeholders (in a real app, this would use Chart.js or similar)
document.addEventListener('DOMContentLoaded', () => {
    // Create simple visualizations for the charts
    createSimpleChart('weight-chart', 'Weight (lbs)', [175, 174, 173, 173, 172, 172]);
    createSimpleChart('workout-chart', 'Workouts per Week', [3, 4, 5, 4, 5, 4]);
    createSimpleChart('calories-chart', 'Calories Burned', [320, 450, 380, 520, 410, 480]);
});

// Simple chart creation function
function createSimpleChart(canvasId, label, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw chart title
    ctx.fillStyle = '#2e7d32';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(label, width / 2, 20);
    
    // Draw chart
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    
    // Find min and max values
    const minValue = Math.min(...data);
    const maxValue = Math.max(...data);
    const valueRange = maxValue - minValue || 1; // Prevent division by zero
    
    // Calculate step size for x-axis
    const stepX = chartWidth / (data.length - 1);
    
    // Draw axes
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding); // X-axis
    ctx.lineTo(width - padding, padding); // Y-axis
    ctx.stroke();
    
    // Draw data points and lines
    ctx.strokeStyle = '#2e7d32';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for (let i = 0; i < data.length; i++) {
        const x = padding + i * stepX;
        const y = height - padding - ((data[i] - minValue) / valueRange) * chartHeight;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        // Draw point
        ctx.fillStyle = '#2e7d32';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    }
    
    ctx.stroke();
}