const PRODUCTS = [
    { id: 1, name: 'Noir Silk Blazer', price: 850, image: 'https://images.unsplash.com/photo-1591047139829-d95777367676?auto=format&fit=crop&w=800&q=80' },
    { id: 2, name: 'Ivory Cashmere Knit', price: 420, image: 'https://images.unsplash.com/photo-1576528647589-C77769277226?auto=format&fit=crop&w=800&q=80' },
    { id: 3, name: 'Studio Tailored Trousers', price: 310, image: 'https://images.unsplash.com/photo-1594633926227-d4b235d6932b?auto=format&fit=crop&w=800&q=80' },
    { id: 4, name: 'Minimalist Leather Tote', price: 1200, image: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80' },
    { id: 5, name: 'Sleek Monochrome Watch', price: 2100, image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80' },
    { id: 6, name: 'Architectural Heel', price: 680, image: 'https://images.unsplash.com/photo-1543163521-16127f6576bc?auto=format&fit=crop&w=800&q=80' },
];

let cart = [];

function init() {
    renderProducts();
    setupEventListeners();
}

function renderProducts() {
    const grid = document.getElementById('productGrid');
    grid.innerHTML = PRODUCTS.map(p => `
        <div class="product-card" onclick="addToCart(${p.id})">
            <img src="${p.image}" class="product-image" alt="${p.name}">
            <div class="product-info">
                <span class="product-name">${p.name}</span>
                <span class="product-price">$${p.price}</span>
            </div>
        </div>
    `).join('');
}

function addToCart(id) {
    const product = PRODUCTS.find(p => p.id === id);
    cart.push(product);
    updateCart();
    openCart();
}

function updateCart() {
    const count = document.querySelector('.cart-count');
    const itemsContainer = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    
    count.textContent = cart.length;
    
    itemsContainer.innerHTML = cart.map((item, index) => `
        <div class="cart-item">
            <img src="${item.image}" alt="${item.name}">
            <div>
                <div style="font-weight:600">${item.name}</div>
                <div style="font-size:0.8rem; color:#666">$${item.price}</div>
            </div>
            <span style="cursor:pointer" onclick="removeFromCart(${index})">&times;</span>
        </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    totalEl.textContent = `$${total.toLocaleString()}`;
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
}

function openCart() {
    document.getElementById('cartOverlay').classList.add('active');
    document.getElementById('cartPanel').classList.add('active');
}

function closeCart() {
    document.getElementById('cartOverlay').classList.remove('active');
    document.getElementById('cartPanel').classList.remove('active');
}

function setupEventListeners() {
    document.getElementById('cartBtn').addEventListener('click', openCart);
    document.getElementById('closeCart').addEventListener('click', closeCart);
    document.getElementById('cartOverlay').addEventListener('click', closeCart);
    
    window.addEventListener('scroll', () => {
        const nav = document.getElementById('mainNav');
        if (window.scrollY > 50) nav.classList.add('scrolled');
        else nav.classList.remove('scrolled');
    });
}

window.addToCart = addToCart;
window.removeFromCart = removeFromCart;

init();
