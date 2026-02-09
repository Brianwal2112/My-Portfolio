// Sample product data with local images
const products = [
    {
        id: 1,
        title: "Wireless Headphones",
        price: 89.99,
        category: "electronics",
        image: "images/headphones.jpg",
        description: "High-quality wireless headphones with active noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers and professionals.",
        inStock: true,
        rating: 4.5
    },
    {
        id: 2,
        title: "Smart Watch",
        price: 199.99,
        category: "electronics",
        image: "images/smartwatch.jpg",
        description: "Feature-rich smartwatch with health monitoring, GPS tracking, heart rate monitor, and 7-day battery life. Water-resistant up to 50 meters.",
        inStock: true,
        rating: 4.8
    },
    {
        id: 3,
        title: "Cotton T-Shirt",
        price: 19.99,
        category: "clothing",
        image: "images/tshirt.jpg",
        description: "Comfortable 100% organic cotton t-shirt available in multiple colors. Soft, breathable, and perfect for everyday wear. Machine washable.",
        inStock: true,
        rating: 4.2
    },
    {
        id: 4,
        title: "Coffee Maker",
        price: 79.99,
        category: "home",
        image: "images/coffeemaker.jpg",
        description: "Programmable 12-cup coffee maker with thermal carafe, auto-shutoff, and brew strength control. Keeps coffee hot for hours.",
        inStock: true,
        rating: 4.6
    },
    {
        id: 5,
        title: "Bestseller Novel",
        price: 14.99,
        category: "books",
        image: "images/book.jpg",
        description: "Award-winning novel that everyone is talking about. 400 pages of captivating storytelling. Hardcover edition with dust jacket.",
        inStock: true,
        rating: 4.7
    },
    {
        id: 6,
        title: "Running Shoes",
        price: 129.99,
        category: "clothing",
        image: "images/shoes.jpg",
        description: "Lightweight running shoes with extra cushioning, breathable mesh upper, and durable rubber outsole. Available in sizes 7-13.",
        inStock: true,
        rating: 4.4
    },
    {
        id: 7,
        title: "Blender",
        price: 59.99,
        category: "home",
        image: "images/blender.jpg",
        description: "Powerful 700W blender for smoothies and food prep. 5-speed settings with pulse function. 64oz BPA-free pitcher included.",
        inStock: false,
        rating: 4.3
    },
    {
        id: 8,
        title: "Programming Book",
        price: 39.99,
        category: "books",
        image: "images/programming-book.jpg",
        description: "Comprehensive guide to modern programming techniques. 800 pages covering JavaScript, Python, and more. Includes online code repository.",
        inStock: true,
        rating: 4.9
    },
    {
        id: 9,
        title: "Laptop Backpack",
        price: 49.99,
        category: "electronics",
        image: "images/backpack.jpg",
        description: "Water-resistant laptop backpack fits up to 15.6\" laptops. Multiple compartments, USB charging port, and anti-theft design.",
        inStock: true,
        rating: 4.5
    },
    {
        id: 10,
        title: "Yoga Mat",
        price: 29.99,
        category: "home",
        image: "images/yoga-mat.jpg",
        description: "Premium 6mm thick yoga mat with non-slip surface. Eco-friendly TPE material. Includes carrying strap. 72\" x 24\".",
        inStock: true,
        rating: 4.6
    },
    {
        id: 11,
        title: "Denim Jacket",
        price: 59.99,
        category: "clothing",
        image: "images/denim-jacket.jpg",
        description: "Classic denim jacket with vintage wash. 100% cotton denim with button closure. Available in sizes S-XXL.",
        inStock: true,
        rating: 4.3
    },
    {
        id: 12,
        title: "Cookbook",
        price: 24.99,
        category: "books",
        image: "images/cookbook.jpg",
        description: "200+ easy recipes for busy people. Beautifully illustrated with step-by-step instructions. Hardcover, 300 pages.",
        inStock: true,
        rating: 4.4
    }
];

// Cart functionality
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// DOM Elements
const cartCountEl = document.getElementById('cart-count');
const featuredProductsEl = document.getElementById('featured-products');
const allProductsEl = document.getElementById('all-products');
const cartItemsEl = document.getElementById('cart-items');
const emptyCartMessageEl = document.getElementById('empty-cart-message');
const subtotalEl = document.getElementById('subtotal');
const totalEl = document.getElementById('total');

// Search functionality
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    displayFeaturedProducts();
    displayAllProducts();
    displayCartItems();
    updateCartSummary();

    // Add event listeners for category filter
    const categoryFilter = document.getElementById('category-filter');
    if(categoryFilter) {
        categoryFilter.addEventListener('change', () => {
            const selectedCategory = categoryFilter.value;
            const searchTerm = searchInput ? searchInput.value : '';
            displayAllProducts(selectedCategory, searchTerm);
        });
    }

    // Add event listeners for search
    if(searchInput) {
        searchInput.addEventListener('input', (e) => {
            const categoryFilter = document.getElementById('category-filter');
            const selectedCategory = categoryFilter ? categoryFilter.value : 'all';
            displayAllProducts(selectedCategory, e.target.value);
        });
    }

    if(searchBtn) {
        searchBtn.addEventListener('click', () => {
            const categoryFilter = document.getElementById('category-filter');
            const selectedCategory = categoryFilter ? categoryFilter.value : 'all';
            displayAllProducts(selectedCategory, searchInput.value);
        });
    }

    // Add event listener for checkout button
    const checkoutBtn = document.getElementById('checkout-btn');
    if(checkoutBtn) {
        checkoutBtn.addEventListener('click', handleCheckout);
    }

    // Close modal when clicking outside
    const modal = document.getElementById('product-modal');
    if(modal) {
        modal.addEventListener('click', (e) => {
            if(e.target === modal) {
                closeProductModal();
            }
        });
    }
});

// Display featured products on homepage
function displayFeaturedProducts() {
    if(!featuredProductsEl) return;

    // Get first 4 in-stock products as featured
    const featured = products.filter(p => p.inStock).slice(0, 4);

    featuredProductsEl.innerHTML = featured.map(product => `
        <div class="product-card" onclick="openProductModal(${product.id})">
            <div class="product-image-container">
                <img src="${product.image}" alt="${product.title}" class="product-image" loading="lazy">
                ${!product.inStock ? '<span class="out-of-stock-badge">Out of Stock</span>' : ''}
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-rating">${generateStars(product.rating)}</div>
                <div class="product-price">$${product.price.toFixed(2)}</div>
                <div class="product-category">${formatCategory(product.category)}</div>
                <button class="add-to-cart" onclick="event.stopPropagation(); addToCart(${product.id})" ${!product.inStock ? 'disabled' : ''}>
                    ${product.inStock ? 'Add to Cart' : 'Out of Stock'}
                </button>
            </div>
        </div>
    `).join('');
}

// Display all products with optional category filter and search
function displayAllProducts(category = 'all', searchTerm = '') {
    if(!allProductsEl) return;

    let filteredProducts = products;

    // Filter by category
    if(category !== 'all') {
        filteredProducts = filteredProducts.filter(product => product.category === category);
    }

    // Filter by search term
    if(searchTerm.trim()) {
        const term = searchTerm.toLowerCase();
        filteredProducts = filteredProducts.filter(product =>
            product.title.toLowerCase().includes(term) ||
            product.description.toLowerCase().includes(term) ||
            product.category.toLowerCase().includes(term)
        );
    }

    // Show message if no products found
    if(filteredProducts.length === 0) {
        allProductsEl.innerHTML = `
            <div class="no-products">
                <p>No products found matching your criteria.</p>
                <button class="btn" onclick="resetFilters()">Reset Filters</button>
            </div>
        `;
        return;
    }

    allProductsEl.innerHTML = filteredProducts.map(product => `
        <div class="product-card" onclick="openProductModal(${product.id})">
            <div class="product-image-container">
                <img src="${product.image}" alt="${product.title}" class="product-image" loading="lazy">
                ${!product.inStock ? '<span class="out-of-stock-badge">Out of Stock</span>' : ''}
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-rating">${generateStars(product.rating)}</div>
                <div class="product-price">$${product.price.toFixed(2)}</div>
                <div class="product-category">${formatCategory(product.category)}</div>
                <button class="add-to-cart" onclick="event.stopPropagation(); addToCart(${product.id})" ${!product.inStock ? 'disabled' : ''}>
                    ${product.inStock ? 'Add to Cart' : 'Out of Stock'}
                </button>
            </div>
        </div>
    `).join('');
}

// Reset filters
function resetFilters() {
    const categoryFilter = document.getElementById('category-filter');
    if(categoryFilter) categoryFilter.value = 'all';
    if(searchInput) searchInput.value = '';
    displayAllProducts('all', '');
}

// Generate star rating HTML
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    let stars = '';
    for(let i = 0; i < fullStars; i++) {
        stars += '<span class="star full">★</span>';
    }
    if(hasHalfStar) {
        stars += '<span class="star half">★</span>';
    }
    for(let i = 0; i < emptyStars; i++) {
        stars += '<span class="star empty">☆</span>';
    }
    return stars;
}

// Format category name
function formatCategory(category) {
    return category.charAt(0).toUpperCase() + category.slice(1);
}

// Open product modal
function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if(!product) return;

    const modal = document.getElementById('product-modal');
    const modalContent = document.getElementById('modal-product-details');

    if(!modal || !modalContent) return;

    modalContent.innerHTML = `
        <div class="modal-product">
            <div class="modal-product-image">
                <img src="${product.image}" alt="${product.title}">
            </div>
            <div class="modal-product-info">
                <h2>${product.title}</h2>
                <div class="modal-product-rating">${generateStars(product.rating)} <span>(${product.rating}/5)</span></div>
                <div class="modal-product-price">$${product.price.toFixed(2)}</div>
                <div class="modal-product-category">${formatCategory(product.category)}</div>
                <div class="modal-product-description">
                    <h3>Description</h3>
                    <p>${product.description}</p>
                </div>
                <div class="modal-product-stock ${product.inStock ? 'in-stock' : 'out-of-stock'}">
                    ${product.inStock ? '✓ In Stock' : '✗ Out of Stock'}
                </div>
                <button class="btn add-to-cart-btn" onclick="addToCart(${product.id}); closeProductModal();" ${!product.inStock ? 'disabled' : ''}>
                    ${product.inStock ? 'Add to Cart' : 'Out of Stock'}
                </button>
            </div>
        </div>
    `;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close product modal
function closeProductModal() {
    const modal = document.getElementById('product-modal');
    if(modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Add item to cart
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    // Check if product is already in cart
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: product.id,
            title: product.title,
            price: product.price,
            image: product.image,
            quantity: 1
        });
    }
    
    // Save cart to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Update UI
    updateCartCount();
    displayCartItems();
    updateCartSummary();
    
    // Show notification
    showNotification(`${product.title} added to cart!`);
}

// Remove item from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCartItems();
    updateCartSummary();
}

// Update item quantity in cart
function updateQuantity(productId, newQuantity) {
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = newQuantity;
        localStorage.setItem('cart', JSON.stringify(cart));
        displayCartItems();
        updateCartSummary();
    }
}

// Display cart items
function displayCartItems() {
    if(!cartItemsEl) return;

    if (cart.length === 0) {
        cartItemsEl.style.display = 'none';
        if(emptyCartMessageEl) emptyCartMessageEl.style.display = 'block';
        // Hide cart summary when empty
        const cartSummary = document.querySelector('.cart-summary');
        if(cartSummary) cartSummary.style.display = 'none';
        return;
    }

    cartItemsEl.style.display = 'block';
    if(emptyCartMessageEl) emptyCartMessageEl.style.display = 'none';
    // Show cart summary
    const cartSummary = document.querySelector('.cart-summary');
    if(cartSummary) cartSummary.style.display = 'block';

    cartItemsEl.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="${item.image}" alt="${item.title}" class="cart-item-image">
            <div class="cart-item-details">
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)} each</div>
                <div class="cart-item-subtotal">Subtotal: $${(item.price * item.quantity).toFixed(2)}</div>
                <div class="cart-item-quantity">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                    <input type="number" class="quantity-input" value="${item.quantity}" min="1" onchange="updateQuantity(${item.id}, parseInt(this.value))">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">Remove</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Update cart count in navbar
function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    if(cartCountEl) {
        cartCountEl.textContent = count;
    }
}

// Update cart summary
function updateCartSummary() {
    if(!subtotalEl || !totalEl) return;
    
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = subtotal > 0 ? 5.99 : 0;
    const total = subtotal + shipping;
    
    subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    totalEl.textContent = `$${total.toFixed(2)}`;
}

// Handle checkout process
function handleCheckout() {
    if (cart.length === 0) {
        showNotification('Your cart is empty!');
        return;
    }

    // Open checkout modal
    openCheckoutModal();
}

// Open checkout modal
function openCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    const modalContent = document.getElementById('checkout-form-container');

    if(!modal || !modalContent) {
        // Fallback to simple alert if modal doesn't exist
        const total = document.getElementById('total').textContent;
        if(confirm(`Proceed with checkout? Total: ${total}`)) {
            completeCheckout();
        }
        return;
    }

    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = 5.99;
    const total = subtotal + shipping;

    modalContent.innerHTML = `
        <div class="checkout-form">
            <h2>Checkout</h2>
            <div class="checkout-summary">
                <h3>Order Summary</h3>
                ${cart.map(item => `
                    <div class="checkout-item">
                        <span>${item.title} x ${item.quantity}</span>
                        <span>$${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                `).join('')}
                <div class="checkout-totals">
                    <div class="checkout-row">
                        <span>Subtotal:</span>
                        <span>$${subtotal.toFixed(2)}</span>
                    </div>
                    <div class="checkout-row">
                        <span>Shipping:</span>
                        <span>$${shipping.toFixed(2)}</span>
                    </div>
                    <div class="checkout-row total">
                        <span>Total:</span>
                        <span>$${total.toFixed(2)}</span>
                    </div>
                </div>
            </div>
            <form id="checkout-form" onsubmit="event.preventDefault(); processCheckout();">
                <h3>Shipping Information</h3>
                <div class="form-group">
                    <label for="checkout-name">Full Name *</label>
                    <input type="text" id="checkout-name" required placeholder="John Doe">
                </div>
                <div class="form-group">
                    <label for="checkout-email">Email *</label>
                    <input type="email" id="checkout-email" required placeholder="john@example.com">
                </div>
                <div class="form-group">
                    <label for="checkout-address">Address *</label>
                    <input type="text" id="checkout-address" required placeholder="123 Main St">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="checkout-city">City *</label>
                        <input type="text" id="checkout-city" required placeholder="New York">
                    </div>
                    <div class="form-group">
                        <label for="checkout-zip">ZIP Code *</label>
                        <input type="text" id="checkout-zip" required placeholder="10001" pattern="[0-9]*">
                    </div>
                </div>
                <h3>Payment Information</h3>
                <div class="form-group">
                    <label for="checkout-card">Card Number *</label>
                    <input type="text" id="checkout-card" required placeholder="1234 5678 9012 3456" maxlength="19">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="checkout-expiry">Expiry Date *</label>
                        <input type="text" id="checkout-expiry" required placeholder="MM/YY" maxlength="5">
                    </div>
                    <div class="form-group">
                        <label for="checkout-cvv">CVV *</label>
                        <input type="text" id="checkout-cvv" required placeholder="123" maxlength="4">
                    </div>
                </div>
                <div class="checkout-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeCheckoutModal()">Cancel</button>
                    <button type="submit" class="btn checkout-btn">Place Order - $${total.toFixed(2)}</button>
                </div>
            </form>
        </div>
    `;

    // Add card formatting
    const cardInput = document.getElementById('checkout-card');
    if(cardInput) {
        cardInput.addEventListener('input', formatCardNumber);
    }

    const expiryInput = document.getElementById('checkout-expiry');
    if(expiryInput) {
        expiryInput.addEventListener('input', formatExpiry);
    }

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close checkout modal
function closeCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if(modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Format card number
function formatCardNumber(e) {
    let value = e.target.value.replace(/\s/g, '');
    value = value.replace(/\D/g, '');
    value = value.substring(0, 16);
    const parts = value.match(/.{1,4}/g);
    e.target.value = parts ? parts.join(' ') : value;
}

// Format expiry date
function formatExpiry(e) {
    let value = e.target.value.replace(/\D/g, '');
    value = value.substring(0, 4);
    if(value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2);
    }
    e.target.value = value;
}

// Process checkout
function processCheckout() {
    const name = document.getElementById('checkout-name').value;
    const email = document.getElementById('checkout-email').value;

    // Simulate processing
    const submitBtn = document.querySelector('#checkout-form button[type="submit"]');
    if(submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
    }

    setTimeout(() => {
        closeCheckoutModal();
        completeCheckout(name, email);
    }, 1500);
}

// Complete checkout
function completeCheckout(customerName = '', customerEmail = '') {
    const total = document.getElementById('total').textContent;

    // Clear cart after checkout
    cart = [];
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCartItems();
    updateCartSummary();

    // Show success modal
    showOrderSuccessModal(customerName, total);
}

// Show order success modal
function showOrderSuccessModal(customerName, total) {
    const modal = document.getElementById('checkout-modal');
    const modalContent = document.getElementById('checkout-form-container');

    if(modal && modalContent) {
        modalContent.innerHTML = `
            <div class="order-success">
                <div class="success-icon">✓</div>
                <h2>Order Placed Successfully!</h2>
                <p>Thank you${customerName ? ', ' + customerName : ''} for your order.</p>
                <p class="order-total">Total: ${total}</p>
                <p class="order-confirmation">A confirmation email has been sent to your email address.</p>
                <button class="btn" onclick="closeCheckoutModal()">Continue Shopping</button>
            </div>
        `;
        modal.style.display = 'block';
    } else {
        showNotification('Order placed successfully!');
    }
}

// Show notification
function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span class="notification-message">${message}</span>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}