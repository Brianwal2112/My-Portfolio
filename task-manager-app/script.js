// Sample tasks data
let tasks = JSON.parse(localStorage.getItem('tasks')) || [
    {
        id: 1,
        title: "Complete project proposal",
        description: "Finish the proposal document for the client meeting",
        dueDate: "2026-06-15",
        priority: "high",
        completed: false,
        assignedTo: "John Doe"
    },
    {
        id: 2,
        title: "Review design mockups",
        description: "Provide feedback on the new UI designs",
        dueDate: "2026-06-10",
        priority: "medium",
        completed: false,
        assignedTo: "Jane Smith"
    },
    {
        id: 3,
        title: "Prepare presentation",
        description: "Create slides for the quarterly review",
        dueDate: "2026-06-05",
        priority: "high",
        completed: true,
        assignedTo: "Robert Brown"
    }
];

// DOM Elements
const taskForm = document.getElementById('task-form');
const tasksList = document.getElementById('tasks-list');
const recentTasksList = document.getElementById('recent-tasks-list');
const totalTasksEl = document.getElementById('total-tasks');
const completedTasksEl = document.getElementById('completed-tasks');
const pendingTasksEl = document.getElementById('pending-tasks');
const overdueTasksEl = document.getElementById('overdue-tasks');
const calendarDaysEl = document.getElementById('calendar-days');
const currentMonthYearEl = document.getElementById('current-month-year');
const upcomingTasksList = document.getElementById('upcoming-tasks-list');
const teamTasksList = document.getElementById('team-tasks-list');

// Current date for calendar
let currentDate = new Date();

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    if(taskForm) {
        taskForm.addEventListener('submit', addTask);
    }
    
    updateStats();
    displayRecentTasks();
    displayAllTasks();
    
    if(calendarDaysEl) {
        renderCalendar(currentDate);
    }
    
    displayUpcomingTasks();
    displayTeamTasks();
    
    // Add event listeners for calendar navigation
    document.getElementById('prev-month')?.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });
    
    document.getElementById('next-month')?.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });
    
    // Add event listeners for filters
    document.getElementById('status-filter')?.addEventListener('change', displayAllTasks);
    document.getElementById('priority-filter')?.addEventListener('change', displayAllTasks);
});

// Add a new task
function addTask(e) {
    e.preventDefault();
    
    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-desc').value;
    const dueDate = document.getElementById('task-due-date').value;
    const priority = document.getElementById('task-priority').value;
    
    if (!title) return;
    
    const newTask = {
        id: Date.now(),
        title,
        description,
        dueDate,
        priority,
        completed: false,
        assignedTo: "Me" // Default assignment
    };
    
    tasks.push(newTask);
    localStorage.setItem('tasks', JSON.stringify(tasks));
    
    // Reset form
    taskForm.reset();
    
    // Update UI
    updateStats();
    displayRecentTasks();
    displayAllTasks();
    displayUpcomingTasks();
    displayTeamTasks();
    
    // Show notification
    showNotification(`${title} added to tasks!`);
}

// Toggle task completion
function toggleTaskCompletion(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        task.completed = !task.completed;
        localStorage.setItem('tasks', JSON.stringify(tasks));
        updateStats();
        displayRecentTasks();
        displayAllTasks();
        displayUpcomingTasks();
        displayTeamTasks();
    }
}

// Delete a task
function deleteTask(id) {
    if (confirm('Are you sure you want to delete this task?')) {
        tasks = tasks.filter(t => t.id !== id);
        localStorage.setItem('tasks', JSON.stringify(tasks));
        updateStats();
        displayRecentTasks();
        displayAllTasks();
        displayUpcomingTasks();
        displayTeamTasks();
        showNotification('Task deleted');
    }
}

// Update task
function updateTask(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        const newTitle = prompt('Update task title:', task.title);
        if (newTitle) {
            task.title = newTitle;
            localStorage.setItem('tasks', JSON.stringify(tasks));
            displayRecentTasks();
            displayAllTasks();
            displayUpcomingTasks();
            displayTeamTasks();
            showNotification('Task updated');
        }
    }
}

// Update statistics
function updateStats() {
    if(!totalTasksEl || !completedTasksEl || !pendingTasksEl || !overdueTasksEl) return;
    
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const pending = tasks.filter(t => !t.completed).length;
    const today = new Date();
    const overdue = tasks.filter(t => {
        if (t.completed) return false;
        const dueDate = new Date(t.dueDate);
        return dueDate < today;
    }).length;
    
    totalTasksEl.textContent = total;
    completedTasksEl.textContent = completed;
    pendingTasksEl.textContent = pending;
    overdueTasksEl.textContent = overdue;
}

// Display recent tasks
function displayRecentTasks() {
    if(!recentTasksList) return;
    
    const recent = [...tasks]
        .sort((a, b) => new Date(b.dueDate) - new Date(a.dueDate))
        .slice(0, 5); // Get 5 most recent tasks
    
    recentTasksList.innerHTML = recent.map(task => `
        <div class="task-item">
            <div class="task-info">
                <div class="task-title">${task.title}</div>
                <div class="task-desc">${task.description}</div>
                <div class="task-meta">
                    <span>Due: ${formatDate(task.dueDate)}</span>
                    <span>Priority: ${task.priority}</span>
                    <span>${task.completed ? '✓ Completed' : '○ Pending'}</span>
                </div>
            </div>
            <div class="task-actions">
                <button class="action-btn complete-btn" onclick="toggleTaskCompletion(${task.id})">
                    ${task.completed ? 'Undo' : 'Complete'}
                </button>
                <button class="action-btn edit-btn" onclick="updateTask(${task.id})">Edit</button>
                <button class="action-btn delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Display all tasks with filtering
function displayAllTasks() {
    if(!tasksList) return;
    
    let filteredTasks = [...tasks];
    
    // Apply status filter
    const statusFilter = document.getElementById('status-filter')?.value;
    if (statusFilter && statusFilter !== 'all') {
        if (statusFilter === 'completed') {
            filteredTasks = filteredTasks.filter(t => t.completed);
        } else if (statusFilter === 'pending') {
            filteredTasks = filteredTasks.filter(t => !t.completed);
        } else if (statusFilter === 'overdue') {
            const today = new Date();
            filteredTasks = filteredTasks.filter(t => {
                if (t.completed) return false;
                const dueDate = new Date(t.dueDate);
                return dueDate < today;
            });
        }
    }
    
    // Apply priority filter
    const priorityFilter = document.getElementById('priority-filter')?.value;
    if (priorityFilter && priorityFilter !== 'all') {
        filteredTasks = filteredTasks.filter(t => t.priority === priorityFilter);
    }
    
    // Sort by due date
    filteredTasks.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
    
    tasksList.innerHTML = filteredTasks.map(task => `
        <div class="task-card ${task.completed ? 'completed' : ''} ${isOverdue(task) ? 'overdue' : ''} ${task.priority}-priority">
            <div class="task-card-header">
                <div class="task-card-title">${task.title}</div>
                <div class="task-card-actions">
                    <button class="action-btn complete-btn" onclick="toggleTaskCompletion(${task.id})">
                        ${task.completed ? 'Undo' : 'Complete'}
                    </button>
                    <button class="action-btn delete-btn" onclick="deleteTask(${task.id})">Delete</button>
                </div>
            </div>
            <div class="task-card-body">
                <div class="task-card-desc">${task.description}</div>
            </div>
            <div class="task-card-footer">
                <span>Due: ${formatDate(task.dueDate)}</span>
                <span>Priority: ${task.priority}</span>
                <span>Assigned to: ${task.assignedTo}</span>
            </div>
        </div>
    `).join('');
}

// Display upcoming tasks for calendar
function displayUpcomingTasks() {
    if(!upcomingTasksList) return;
    
    const upcoming = [...tasks]
        .filter(t => !t.completed)
        .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
        .slice(0, 5); // Get 5 upcoming tasks
    
    upcomingTasksList.innerHTML = upcoming.map(task => `
        <div class="task-item">
            <div class="task-info">
                <div class="task-title">${task.title}</div>
                <div class="task-meta">
                    <span>Due: ${formatDate(task.dueDate)}</span>
                    <span>Priority: ${task.priority}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Display team tasks
function displayTeamTasks() {
    if(!teamTasksList) return;
    
    const teamTasks = tasks.slice(0, 5); // Show first 5 tasks
    
    teamTasksList.innerHTML = teamTasks.map(task => `
        <div class="task-item">
            <div class="task-info">
                <div class="task-title">${task.title}</div>
                <div class="task-desc">${task.description}</div>
                <div class="task-meta">
                    <span>Due: ${formatDate(task.dueDate)}</span>
                    <span>Priority: ${task.priority}</span>
                    <span>Assigned to: ${task.assignedTo}</span>
                    <span>${task.completed ? '✓ Completed' : '○ Pending'}</span>
                </div>
            </div>
            <div class="task-actions">
                <button class="action-btn complete-btn" onclick="toggleTaskCompletion(${task.id})">
                    ${task.completed ? 'Undo' : 'Complete'}
                </button>
            </div>
        </div>
    `).join('');
}

// Render calendar
function renderCalendar(date) {
    if(!calendarDaysEl || !currentMonthYearEl) return;
    
    const year = date.getFullYear();
    const month = date.getMonth();
    
    // Set the month/year header
    currentMonthYearEl.textContent = `${date.toLocaleString('default', { month: 'long' })} ${year}`;
    
    // Get the first day of the month and the number of days in the month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    // Get the day of the week for the first day (0 = Sunday, 1 = Monday, etc.)
    const firstDayOfWeek = firstDay.getDay();
    
    // Clear the calendar
    calendarDaysEl.innerHTML = '';
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfWeek; i++) {
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        const dayNum = prevMonthLastDay - firstDayOfWeek + i + 1;
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day other-month';
        dayEl.innerHTML = `<div class="day-number">${dayNum}</div>`;
        calendarDaysEl.appendChild(dayEl);
    }
    
    // Add cells for each day of the month
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const dayEl = document.createElement('div');
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        
        // Check if this day is today
        const isToday = today.getFullYear() === year && 
                       today.getMonth() === month && 
                       today.getDate() === day;
        
        // Check if this day has tasks
        const dayHasEvents = tasks.some(task => task.dueDate === dateStr && !task.completed);
        
        dayEl.className = `calendar-day ${isToday ? 'today' : ''} ${dayHasEvents ? 'has-events' : ''}`;
        
        // Add the day number
        dayEl.innerHTML = `<div class="day-number">${day}</div>`;
        
        // Add events for this day
        const dayEvents = tasks.filter(task => task.dueDate === dateStr && !task.completed);
        if (dayEvents.length > 0) {
            const eventsDiv = document.createElement('div');
            eventsDiv.className = 'day-events';
            dayEvents.forEach(event => {
                const eventBadge = document.createElement('span');
                eventBadge.className = 'event-badge';
                eventBadge.textContent = event.title.substring(0, 20) + (event.title.length > 20 ? '...' : '');
                eventsDiv.appendChild(eventBadge);
            });
            dayEl.appendChild(eventsDiv);
        }
        
        calendarDaysEl.appendChild(dayEl);
    }
    
    // Add empty cells for days after the last day of the month
    const lastDayOfWeek = lastDay.getDay();
    for (let i = lastDayOfWeek + 1; i < 7; i++) {
        const dayNum = i - lastDayOfWeek;
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day other-month';
        dayEl.innerHTML = `<div class="day-number">${dayNum}</div>`;
        calendarDaysEl.appendChild(dayEl);
    }
}

// Helper function to check if a task is overdue
function isOverdue(task) {
    if (task.completed) return false;
    const dueDate = new Date(task.dueDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Set time to beginning of day
    return dueDate < today;
}

// Helper function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#4CAF50';
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