// Sample product data
const products = [
    {
        id: 1,
        title: "Wireless Headphones",
        price: 89.99,
        category: "electronics",
        image: "https://source.unsplash.com/random/300x300/?headphones",
        description: "High-quality wireless headphones with noise cancellation."
    },
    {
        id: 2,
        title: "Smart Watch",
        price: 199.99,
        category: "electronics",
        image: "https://source.unsplash.com/random/300x300/?smartwatch",
        description: "Feature-rich smartwatch with health monitoring."
    },
    {
        id: 3,
        title: "Cotton T-Shirt",
        price: 19.99,
        category: "clothing",
        image: "https://source.unsplash.com/random/300x300/?tshirt",
        description: "Comfortable cotton t-shirt available in multiple colors."
    },
    {
        id: 4,
        title: "Coffee Maker",
        price: 79.99,
        category: "home",
        image: "https://source.unsplash.com/random/300x300/?coffee-maker",
        description: "Programmable coffee maker with thermal carafe."
    },
    {
        id: 5,
        title: "Bestseller Novel",
        price: 14.99,
        category: "books",
        image: "https://source.unsplash.com/random/300x300/?book",
        description: "Award-winning novel that everyone is talking about."
    },
    {
        id: 6,
        title: "Running Shoes",
        price: 129.99,
        category: "clothing",
        image: "https://source.unsplash.com/random/300x300/?shoes",
        description: "Lightweight running shoes with extra cushioning."
    },
    {
        id: 7,
        title: "Blender",
        price: 59.99,
        category: "home",
        image: "https://source.unsplash.com/random/300x300/?blender",
        description: "Powerful blender for smoothies and food prep."
    },
    {
        id: 8,
        title: "Programming Book",
        price: 39.99,
        category: "books",
        image: "https://source.unsplash.com/random/300x300/?programming-book",
        description: "Comprehensive guide to modern programming techniques."
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
            displayAllProducts(selectedCategory);
        });
    }
    
    // Add event listener for checkout button
    const checkoutBtn = document.getElementById('checkout-btn');
    if(checkoutBtn) {
        checkoutBtn.addEventListener('click', handleCheckout);
    }
});

// Display featured products on homepage
function displayFeaturedProducts() {
    if(!featuredProductsEl) return;
    
    // Get first 4 products as featured
    const featured = products.slice(0, 4);
    
    featuredProductsEl.innerHTML = featured.map(product => `
        <div class="product-card">
            <img src="${product.image}" alt="${product.title}" class="product-image">
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-price">$${product.price.toFixed(2)}</div>
                <div class="product-category">${product.category}</div>
                <button class="add-to-cart" onclick="addToCart(${product.id})">Add to Cart</button>
            </div>
        </div>
    `).join('');
}

// Display all products with optional category filter
function displayAllProducts(category = 'all') {
    if(!allProductsEl) return;
    
    let filteredProducts = products;
    if(category !== 'all') {
        filteredProducts = products.filter(product => product.category === category);
    }
    
    allProductsEl.innerHTML = filteredProducts.map(product => `
        <div class="product-card">
            <img src="${product.image}" alt="${product.title}" class="product-image">
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-price">$${product.price.toFixed(2)}</div>
                <div class="product-category">${product.category}</div>
                <button class="add-to-cart" onclick="addToCart(${product.id})">Add to Cart</button>
            </div>
        </div>
    `).join('');
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
        emptyCartMessageEl.style.display = 'block';
        return;
    }
    
    cartItemsEl.style.display = 'block';
    emptyCartMessageEl.style.display = 'none';
    
    cartItemsEl.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="${item.image}" alt="${item.title}" class="cart-item-image">
            <div class="cart-item-details">
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)}</div>
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
    
    // In a real application, this would redirect to a checkout page
    alert(`Proceeding to checkout. Total: $${document.getElementById('total').textContent}`);
    
    // Clear cart after checkout
    cart = [];
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCartItems();
    updateCartSummary();
    showNotification('Order placed successfully!');
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