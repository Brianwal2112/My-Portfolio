// Sample weather data
const sampleWeatherData = {
    location: "New York, NY",
    temperature: 75,
    feelsLike: 77,
    description: "Partly Cloudy",
    humidity: 65,
    windSpeed: 8,
    pressure: 30.15,
    icon: "partly-cloudy-day"
};

const sampleHourlyForecast = [
    { time: "Now", temp: 75, icon: "partly-cloudy-day" },
    { time: "1 PM", temp: 76, icon: "sunny" },
    { time: "2 PM", temp: 77, icon: "sunny" },
    { time: "3 PM", temp: 78, icon: "sunny" },
    { time: "4 PM", temp: 77, icon: "partly-cloudy-day" },
    { time: "5 PM", temp: 76, icon: "partly-cloudy-day" },
    { time: "6 PM", temp: 74, icon: "cloudy" },
    { time: "7 PM", temp: 72, icon: "cloudy" },
    { time: "8 PM", temp: 70, icon: "rain" },
    { time: "9 PM", temp: 69, icon: "rain" }
];

const sampleDailyForecast = [
    { day: "Today", high: 78, low: 65, icon: "partly-cloudy-day", desc: "Partly cloudy" },
    { day: "Tue", high: 80, low: 67, icon: "sunny", desc: "Sunny" },
    { day: "Wed", high: 82, low: 68, icon: "sunny", desc: "Sunny" },
    { day: "Thu", high: 79, low: 66, icon: "rain", desc: "Scattered showers" },
    { day: "Fri", high: 76, low: 64, icon: "cloudy", desc: "Cloudy" },
    { day: "Sat", high: 77, low: 65, icon: "partly-cloudy-day", desc: "Partly cloudy" },
    { day: "Sun", high: 79, low: 66, icon: "sunny", desc: "Sunny" }
];

// DOM Elements
const locationEl = document.getElementById('location');
const dateTimeEl = document.getElementById('date-time');
const tempEl = document.getElementById('temp');
const feelsLikeEl = document.getElementById('feels-like');
const descriptionEl = document.getElementById('description');
const humidityEl = document.getElementById('humidity');
const windSpeedEl = document.getElementById('wind-speed');
const pressureEl = document.getElementById('pressure');
const weatherIconImg = document.getElementById('weather-icon-img');
const hourlyForecastContainer = document.getElementById('hourly-forecast-container');
const dailyForecastContainer = document.getElementById('daily-forecast-container');
const cityInput = document.getElementById('city-input');
const searchBtn = document.getElementById('search-btn');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 60000); // Update every minute
    
    displayCurrentWeather(sampleWeatherData);
    displayHourlyForecast(sampleHourlyForecast);
    
    if(dailyForecastContainer) {
        displayDailyForecast(sampleDailyForecast);
    }
    
    if(searchBtn) {
        searchBtn.addEventListener('click', searchWeather);
    }
    
    if(cityInput) {
        cityInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchWeather();
            }
        });
    }
});

// Update date and time
function updateDateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    if(dateTimeEl) {
        dateTimeEl.textContent = now.toLocaleDateString('en-US', options);
    }
}

// Display current weather
function displayCurrentWeather(data) {
    if(locationEl) locationEl.textContent = data.location;
    if(tempEl) tempEl.textContent = data.temperature;
    if(feelsLikeEl) feelsLikeEl.textContent = `${data.feelsLike}°F`;
    if(descriptionEl) descriptionEl.textContent = data.description;
    if(humidityEl) humidityEl.textContent = `${data.humidity}%`;
    if(windSpeedEl) windSpeedEl.textContent = `${data.windSpeed} mph`;
    if(pressureEl) pressureEl.textContent = `${data.pressure} in`;
    
    if(weatherIconImg) {
        // In a real app, this would use actual weather icons
        weatherIconImg.src = `https://source.unsplash.com/100x100/?${data.icon.replace(/-/g, '+')}`;
        weatherIconImg.alt = data.description;
    }
}

// Display hourly forecast
function displayHourlyForecast(forecast) {
    if(!hourlyForecastContainer) return;
    
    hourlyForecastContainer.innerHTML = forecast.map(item => `
        <div class="forecast-item">
            <div class="forecast-time">${item.time}</div>
            <div class="forecast-icon">
                <img src="https://source.unsplash.com/50x50/?${item.icon.replace(/-/g, '+')}" alt="${item.icon}">
            </div>
            <div class="forecast-temp">${item.temp}°F</div>
        </div>
    `).join('');
}

// Display daily forecast
function displayDailyForecast(forecast) {
    if(!dailyForecastContainer) return;
    
    dailyForecastContainer.innerHTML = forecast.map(item => `
        <div class="daily-forecast-item">
            <div class="daily-forecast-day">${item.day}</div>
            <div class="daily-forecast-icon">
                <img src="https://source.unsplash.com/60x60/?${item.icon.replace(/-/g, '+')}" alt="${item.icon}">
            </div>
            <div class="daily-forecast-desc">${item.desc}</div>
            <div class="daily-forecast-high-low">
                <div class="high-temp">H: ${item.high}°</div>
                <div class="low-temp">L: ${item.low}°</div>
            </div>
        </div>
    `).join('');
}

// Search for weather by city
function searchWeather() {
    const city = cityInput.value.trim();
    if (!city) return;
    
    // In a real app, this would fetch from a weather API
    // For now, we'll simulate with sample data
    showNotification(`Showing weather for ${city} (simulated)`);
    
    // Update location display
    if(locationEl) locationEl.textContent = city;
    
    // Generate new sample data based on the city
    const newWeatherData = {
        location: city,
        temperature: Math.floor(Math.random() * 40) + 50, // Random temp between 50-90
        feelsLike: Math.floor(Math.random() * 40) + 50,
        description: getRandomWeatherDescription(),
        humidity: Math.floor(Math.random() * 50) + 30, // Random humidity between 30-80%
        windSpeed: Math.floor(Math.random() * 20) + 5, // Random wind speed 5-25 mph
        pressure: (Math.random() * 2 + 29).toFixed(2), // Random pressure 29-31 in
        icon: getRandomWeatherIcon()
    };
    
    displayCurrentWeather(newWeatherData);
    
    // Generate new hourly forecast
    const newHourlyForecast = generateHourlyForecast();
    displayHourlyForecast(newHourlyForecast);
}

// Get random weather description
function getRandomWeatherDescription() {
    const descriptions = [
        "Sunny", "Clear", "Partly Cloudy", "Mostly Cloudy", 
        "Cloudy", "Light Rain", "Rain", "Thunderstorms", 
        "Scattered Thunderstorms", "Showers", "Light Snow", "Snow"
    ];
    return descriptions[Math.floor(Math.random() * descriptions.length)];
}

// Get random weather icon
function getRandomWeatherIcon() {
    const icons = [
        "sunny", "clear-night", "partly-cloudy-day", "partly-cloudy-night",
        "cloudy", "rain", "thunderstorm", "snow", "fog", "wind"
    ];
    return icons[Math.floor(Math.random() * icons.length)];
}

// Generate hourly forecast
function generateHourlyForecast() {
    const forecast = [];
    const now = new Date();
    
    for (let i = 0; i < 10; i++) {
        const hour = new Date(now.getTime() + i * 60 * 60 * 1000);
        const hourLabel = hour.getHours() === now.getHours() ? 
            "Now" : 
            `${hour.getHours() % 12 || 12} ${hour.getHours() >= 12 ? 'PM' : 'AM'}`;
        
        forecast.push({
            time: hourLabel,
            temp: Math.floor(Math.random() * 20) + 60, // Random temp between 60-80
            icon: getRandomWeatherIcon()
        });
    }
    
    return forecast;
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#0d47a1';
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

// Map type change functionality
document.addEventListener('DOMContentLoaded', () => {
    const mapTypeSelect = document.getElementById('map-type');
    const weatherMapImg = document.getElementById('weather-map');
    
    if(mapTypeSelect && weatherMapImg) {
        mapTypeSelect.addEventListener('change', () => {
            const mapType = mapTypeSelect.value;
            // In a real app, this would load different map images based on type
            weatherMapImg.src = `https://source.unsplash.com/1200x600/?weather,map,${mapType}`;
            showNotification(`Switched to ${mapType} map`);
        });
    }
    
    const refreshMapBtn = document.getElementById('refresh-map');
    if(refreshMapBtn) {
        refreshMapBtn.addEventListener('click', () => {
            const currentMapType = mapTypeSelect ? mapTypeSelect.value : 'temperature';
            weatherMapImg.src = `https://source.unsplash.com/1200x600/?weather,map,${currentMapType}&t=${Date.now()}`;
            showNotification('Map refreshed');
        });
    }
    
    const enableNotificationsBtn = document.getElementById('enable-notifications');
    if(enableNotificationsBtn) {
        enableNotificationsBtn.addEventListener('click', () => {
            showNotification('Weather notifications enabled!');
        });
    }
});