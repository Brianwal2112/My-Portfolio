const PRODUCTS = [
    { id: 1, name: 'Noir Silk Blazer', price: 850, category: 'apparel', image: 'https://images.unsplash.com/photo-1591047139829-d95777367676?auto=format&fit=crop&w=800&q=80', desc: 'Tailored from 100% Italian silk, this blazer defines modern elegance. Perfect for evening gala or high-stakes business.' },
    { id: 2, name: 'Ivory Cashmere Knit', price: 420, category: 'apparel', image: 'https://images.unsplash.com/photo-1576528647589-C77769277226?auto=format&fit=crop&w=800&q=80', desc: 'Pure Mongolian cashmere. A lightweight yet warm essential for the winter wardrobe.' },
    { id: 3, name: 'Studio Tailored Trousers', price: 310, category: 'apparel', image: 'https://images.unsplash.com/photo-1594633926227-d4b235d6932b?auto=format&fit=crop&w=800&q=80', desc: 'Precision cut trousers with a subtle taper. Designed for the modern architectural silhouette.' },
    { id: 4, name: 'Minimalist Leather Tote', price: 1200, category: 'accessories', image: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80', desc: 'Hand-stitched calfskin leather. Unlined for a natural feel, featuring a single internal pocket.' },
    { id: 5, name: 'Sleek Monochrome Watch', price: 2100, category: 'jewelry', image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80', desc: 'Sapphire crystal glass with a matte black titanium case. A timeless piece of engineering.' },
    { id: 6, name: 'Architectural Heel', price: 680, category: 'accessories', image: 'https://images.unsplash.com/photo-1543163521-16127f6576bc?auto=format&fit=crop&w=800&q=80', desc: 'Sculpted heel designed for balance and form. A statement piece for the bold.' },
];

let cart = JSON.parse(localStorage.getItem('luxe-cart')) || [];

function init() {
    renderProducts(PRODUCTS);
    setupEventListeners();
    updateCart();
}

function renderProducts(productsToRender) {
    const grid = document.getElementById('productGrid');
    if(productsToRender.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align:center; margin-top:4rem; color:#666;">No products found in this collection.</p>';
        return;
    }
    grid.innerHTML = productsToRender.map(p => `
        <div class="product-card" onclick="openProduct(${p.id})">
            <img src="${p.image}" class="product-image" alt="${p.name}">
            <div class="product-info">
                <span class="product-name">${p.name}</span>
                <span class="product-price">$${p.price}</span>
            </div>
        </div>
    `).join('');
}

function openProduct(id) {
    const product = PRODUCTS.find(p => p.id === id);
    document.getElementById('modalImage').src = product.image;
    document.getElementById('modalName').textContent = product.name;
    document.getElementById('modalPrice').textContent = `$${product.price}`;
    document.getElementById('modalCategory').textContent = product.category;
    document.getElementById('modalDesc').textContent = product.desc;
    
    document.getElementById('modalAddBtn').onclick = () => {
        addToCart(product.id);
        closeModal();
    };
    
    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

function addToCart(id) {
    const product = PRODUCTS.find(p => p.id === id);
    cart.push(product);
    saveCart();
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
            <div style="display:flex; flex-direction:column; justify-content:center">
                <div style="font-weight:600">${item.name}</div>
                <div style="font-size:0.8rem; color:#666">$${item.price}</div>
            </div>
            <span style="cursor:pointer; font-size:1.5rem" onclick="removeFromCart(${index})">&times;</span>
        </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    totalEl.textContent = `$${total.toLocaleString()}`;
}

function removeFromCart(index) {
    cart.splice(index, 1);
    saveCart();
    updateCart();
}

function saveCart() {
    localStorage.setItem('luxe-cart', JSON.stringify(cart));
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
    document.getElementById('closeModal').addEventListener('click', closeModal);
    
    // Category Filtering
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const cat = e.target.dataset.category;
            const filtered = cat === 'all' ? PRODUCTS : PRODUCTS.filter(p => p.category === cat);
            renderProducts(filtered);
        });
    });

    // Search Functionality
    document.getElementById('productSearch').addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = PRODUCTS.filter(p => p.name.toLowerCase().includes(term) || p.category.toLowerCase().includes(term));
        renderProducts(filtered);
    });
    
    window.addEventListener('scroll', () => {
        const nav = document.getElementById('mainNav');
        if (window.scrollY > 50) nav.classList.add('scrolled');
        else nav.classList.remove('scrolled');
    });
}

window.openProduct = openProduct;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;

init();
