// Sample blog data
let blogPosts = JSON.parse(localStorage.getItem('blogPosts')) || [
    {
        id: 1,
        title: "The Future of Web Development",
        subtitle: "Exploring the latest trends and technologies shaping the future",
        category: "technology",
        tags: ["web-development", "javascript", "future"],
        author: "Alex Johnson",
        date: "2026-06-15",
        content: "Web development has come a long way since the early days of static HTML pages. As we look toward the future, several key trends are shaping the landscape of how we build and interact with web applications.",
        excerpt: "Exploring the latest trends and technologies shaping the future of web development...",
        image: "https://source.unsplash.com/1200x600/?web-development",
        likes: 245,
        readTime: "8 min read"
    },
    {
        id: 2,
        title: "Modern UI/UX Principles",
        subtitle: "Understanding the core principles that make user interfaces intuitive",
        category: "design",
        tags: ["ui", "ux", "design"],
        author: "Sarah Williams",
        date: "2026-06-12",
        content: "User interface and user experience design are crucial aspects of creating successful digital products. Modern UI/UX principles focus on creating intuitive, accessible, and delightful experiences for users.",
        excerpt: "Understanding the core principles that make user interfaces intuitive and engaging...",
        image: "https://source.unsplash.com/1200x600/?ui-design",
        likes: 187,
        readTime: "6 min read"
    },
    {
        id: 3,
        title: "Boosting Your Coding Efficiency",
        subtitle: "Practical tips and tools to improve your coding speed",
        category: "productivity",
        tags: ["productivity", "coding", "efficiency"],
        author: "Michael Chen",
        date: "2026-06-10",
        content: "Coding efficiency is a skill that can be developed with practice and the right tools. In this article, we'll explore practical tips and tools that can help you write code faster and with fewer errors.",
        excerpt: "Practical tips and tools to improve your coding speed and efficiency...",
        image: "https://source.unsplash.com/1200x600/?coding",
        likes: 156,
        readTime: "5 min read"
    }
];

// DOM Elements
const categoryFilter = document.getElementById('category-filter');
const sortPosts = document.getElementById('sort-posts');
const postsGrid = document.querySelector('.posts-grid');
const createPostForm = document.querySelector('.create-post-form');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    displayPosts();
    
    // Add event listeners for filters
    if(categoryFilter) {
        categoryFilter.addEventListener('change', displayPosts);
    }
    
    if(sortPosts) {
        sortPosts.addEventListener('change', displayPosts);
    }
    
    // Add event listener for create post form
    if(createPostForm) {
        createPostForm.addEventListener('submit', createPost);
    }
    
    // Add event listeners for newsletter form
    const newsletterForm = document.querySelector('.newsletter-form');
    if(newsletterForm) {
        newsletterForm.addEventListener('submit', subscribeToNewsletter);
    }
    
    // Add event listeners for contact form
    const contactForm = document.querySelector('.contact-form');
    if(contactForm) {
        contactForm.addEventListener('submit', submitContactForm);
    }
});

// Display posts based on filters
function displayPosts() {
    if(!postsGrid) return;
    
    let filteredPosts = [...blogPosts];
    
    // Apply category filter
    if(categoryFilter) {
        const selectedCategory = categoryFilter.value;
        if(selectedCategory !== 'all') {
            filteredPosts = filteredPosts.filter(post => post.category === selectedCategory);
        }
    }
    
    // Apply sorting
    if(sortPosts) {
        const sortOrder = sortPosts.value;
        if(sortOrder === 'newest') {
            filteredPosts.sort((a, b) => new Date(b.date) - new Date(a.date));
        } else if(sortOrder === 'oldest') {
            filteredPosts.sort((a, b) => new Date(a.date) - new Date(b.date));
        } else if(sortOrder === 'popular') {
            filteredPosts.sort((a, b) => b.likes - a.likes);
        }
    }
    
    postsGrid.innerHTML = filteredPosts.map(post => `
        <article class="post-card">
            <div class="post-image">
                <img src="${post.image}" alt="${post.title}">
            </div>
            <div class="post-content">
                <div class="post-meta">
                    <span class="post-category">${capitalizeFirstLetter(post.category)}</span>
                    <span class="post-date">${formatDate(post.date)}</span>
                </div>
                <h3 class="post-title">${post.title}</h3>
                <p class="post-excerpt">${post.excerpt}</p>
                <div class="post-stats">
                    <span>${post.readTime}</span>
                    <span>${post.likes} likes</span>
                </div>
                <a href="post.html?id=${post.id}" class="read-more">Read More</a>
            </div>
        </article>
    `).join('');
}

// Create a new post
function createPost(e) {
    e.preventDefault();
    
    const title = document.getElementById('post-title').value;
    const subtitle = document.getElementById('post-subtitle').value;
    const category = document.getElementById('post-category').value;
    const tags = document.getElementById('post-tags').value.split(',').map(tag => tag.trim());
    const image = document.getElementById('post-image').value || 'https://source.unsplash.com/1200x600/?blog';
    const content = document.getElementById('post-content').value;
    
    if(!title || !category || !content) {
        showNotification('Please fill in all required fields');
        return;
    }
    
    const newPost = {
        id: Date.now(),
        title,
        subtitle,
        category,
        tags,
        author: "Current Author", // In a real app, this would be the logged-in user
        date: new Date().toISOString().split('T')[0],
        content,
        excerpt: content.substring(0, 150) + '...',
        image,
        likes: 0,
        readTime: estimateReadTime(content)
    };
    
    blogPosts.unshift(newPost);
    localStorage.setItem('blogPosts', JSON.stringify(blogPosts));
    
    // Reset form
    createPostForm.reset();
    
    showNotification('Post published successfully!');
    
    // Redirect to blog page after a delay
    setTimeout(() => {
        window.location.href = 'blog.html';
    }, 2000);
}

// Subscribe to newsletter
function subscribeToNewsletter(e) {
    e.preventDefault();
    const email = e.target.querySelector('input').value;
    
    if(!email) {
        showNotification('Please enter your email address');
        return;
    }
    
    showNotification(`Thank you for subscribing with ${email}!`);
    e.target.reset();
}

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

// Helper function to capitalize first letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Helper function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Helper function to estimate read time
function estimateReadTime(content) {
    const wordsPerMinute = 200;
    const wordCount = content.trim().split(/\s+/).length;
    const minutes = Math.ceil(wordCount / wordsPerMinute);
    return `${minutes} min read`;
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#2c3e50';
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

// Like functionality (would be implemented in a real app)
document.addEventListener('click', (e) => {
    if(e.target.classList.contains('like-btn')) {
        // In a real app, this would increment the like count
        showNotification('Post liked!');
    }
});