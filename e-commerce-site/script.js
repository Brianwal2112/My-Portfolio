const PRODUCTS = [
    // APPAREL - High End Fashion
    { 
        id: 1, name: 'Noir Silk Blazer', price: 850, category: 'apparel', 
        image: 'https://images.unsplash.com/photo-1591047139829-d95777367676?auto=format&fit=crop&w=800&q=80', 
        desc: 'Tailored from 100% Italian silk, this blazer defines modern elegance. A masterclass in minimal tailoring for the modern professional.', 
        bestSeller: true, newArrival: false 
    },
    { 
        id: 2, name: 'Ivory Cashmere Knit', price: 420, category: 'apparel', 
        image: 'https://images.unsplash.com/photo-1576528647589-C77769277226?auto=format&fit=crop&w=800&q=80', 
        desc: 'Pure Mongolian cashmere. Breathable, soft, and timeless. A piece designed to last a lifetime.', 
        bestSeller: false, newArrival: true 
    },
    { 
        id: 3, name: 'Studio Tailored Trousers', price: 310, category: 'apparel', 
        image: 'https://images.unsplash.com/photo-1594633926227-d4b235d6932b?auto=format&fit=crop&w=800&q=80', 
        desc: 'Precision cut trousers with a subtle taper. Crafted from sustainable wool blends.', 
        bestSeller: true, newArrival: false 
    },
    { 
        id: 7, name: 'Midnight Velvet Gown', price: 1400, category: 'apparel', 
        image: 'https://images.unsplash.com/photo-1566174053879-315B377f526f?auto=format&fit=crop&w=800&q=80', 
        desc: 'Hand-stitched midnight velvet. A sculptural piece for evening galas and red-carpet events.', 
        bestSeller: true, newArrival: true 
    },
    { 
        id: 8, name: 'Alabaster Linen Shirt', price: 280, category: 'apparel', 
        image: 'https://images.unsplash.com/photo-1598033129183-c87b67750810?auto=format&fit=crop&w=800&q=80', 
        desc: '100% organic linen. Breathable, lightweight, and effortlessly refined.', 
        bestSeller: false, newArrival: false 
    },

    // ACCESSORIES - Leather & Studio
    { 
        id: 4, name: 'Minimalist Leather Tote', price: 1200, category: 'accessories', 
        image: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80', 
        desc: 'Hand-stitched Italian calfskin leather. Structured, spacious, and unlined for a natural luxury feel.', 
        bestSeller: true, newArrival: false 
    },
    { 
        id: 6, name: 'Architectural Heel', price: 680, category: 'accessories', 
        image: 'https://images.unsplash.com/photo-1543163521-16127f6576bc?auto=format&fit=crop&w=800&q=80', 
        desc: 'Sculpted silhouette designed for balance and poise. A statement piece in modern footwear.', 
        bestSeller: false, newArrival: true 
    },
    { 
        id: 9, name: 'Suede Chelsea Boot', price: 550, category: 'accessories', 
        image: 'https://images.unsplash.com/photo-1638242657605-7ed692672703?auto=format&fit=crop&w=800&q=80', 
        desc: 'Premium water-resistant suede. A timeless silhouette for urban exploration.', 
        bestSeller: false, newArrival: true 
    },
    { 
        id: 10, name: 'Aviator Frame Onyx', price: 320, category: 'accessories', 
        image: 'https://images.unsplash.com/photo-1572635196237-14b3f17dfae0?auto=format&fit=crop&w=800&q=80', 
        desc: 'Polarized lenses with a lightweight titanium frame. The ultimate in visual clarity.', 
        bestSeller: true, newArrival: false 
    },

    // JEWELRY - Fine Metals
    { 
        id: 5, name: 'Sleek Monochrome Watch', price: 2100, category: 'jewelry', 
        image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80', 
        desc: 'Sapphire crystal glass with a matte black titanium case. A timeless piece of engineering.', 
        bestSeller: false, newArrival: true 
    },
    { 
        id: 11, name: 'Gold Orbital Ring', price: 1800, category: 'jewelry', 
        image: 'https://images.unsplash.com/photo-1605100804763-247867157a70?auto=format&fit=crop&w=800&q=80', 
        desc: '18k solid gold with a brushed matte finish. A singular, sculptural statement.', 
        bestSeller: true, newArrival: false 
    },
    { 
        id: 12, name: 'Diamond Studs', price: 3500, category: 'jewelry', 
        image: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60?auto=format&fit=crop&w=800&q=80', 
        desc: 'Conflict-free diamonds set in platinum. Pure, radiant brilliance in a minimal form.', 
        bestSeller: false, newArrival: true 
    },
    { 
        id: 13, name: 'Silver Link Bracelet', price: 720, category: 'jewelry', 
        image: 'https://images.unsplash.com/photo-1611591437289-567d78663949?auto=format&fit=crop&w=800&q=80', 
        desc: 'Hand-linked sterling silver. A balanced blend of strength and elegance.', 
        bestSeller: true, newArrival: false 
    },
];

let cart = JSON.parse(localStorage.getItem('lumina-cart')) || [];

function init() {
    const grid = document.getElementById('productGrid');
    const bestSellersGrid = document.getElementById('bestSellersGrid');
    const newArrivalsGrid = document.getElementById('newArrivalsGrid');

    if (grid) {
        const urlParams = new URLSearchParams(window.location.search);
        const cat = urlParams.get('cat');
        if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
            renderProducts(grid, PRODUCTS.slice(0, 4));
        } else {
            const filtered = cat ? PRODUCTS.filter(p => p.category === cat) : PRODUCTS;
            renderProducts(grid, filtered);
            if (cat) {
                const title = document.getElementById('categoryTitle');
                if (title) title.textContent = cat.charAt(0).toUpperCase() + cat.slice(1) + ' Collection';
            }
        }
    }

    if (bestSellersGrid) {
        renderProducts(bestSellersGrid, PRODUCTS.filter(p => p.bestSeller).slice(0, 4));
    }

    if (newArrivalsGrid) {
        renderProducts(newArrivalsGrid, PRODUCTS.filter(p => p.newArrival).slice(0, 4));
    }

    setupEventListeners();
    updateCart();
}

function renderProducts(gridElement, productsToRender) {
    if(!gridElement) return;
    if(productsToRender.length === 0) {
        gridElement.innerHTML = '<p style="grid-column: 1/-1; text-align:center; margin-top:4rem; color:#666;">No pieces found in this collection.</p>';
        return;
    }
    gridElement.innerHTML = productsToRender.map(p => `
        <div class="product-card" onclick="openProduct(${p.id})">
            <div class="product-image-container">
                <img src="${p.image}" class="product-image" alt="${p.name}">
            </div>
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
    localStorage.setItem('lumina-cart', JSON.stringify(cart));
    updateCart();
    openCart();
}

function updateCart() {
    const count = document.querySelector('.badge');
    const itemsContainer = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    if(count) count.textContent = cart.length;
    if(!itemsContainer) return;
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
    if(totalEl) totalEl.textContent = `$${total.toLocaleString()}`;
}

function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem('lumina-cart', JSON.stringify(cart));
    updateCart();
}

function openCart() {
    document.getElementById('cartOverlay')?.classList.add('active');
    document.getElementById('cartPanel')?.classList.add('active');
}

function closeCart() {
    document.getElementById('cartOverlay')?.classList.remove('active');
    document.getElementById('cartPanel')?.classList.remove('active');
}

function setupEventListeners() {
    document.getElementById('cartBtn')?.addEventListener('click', openCart);
    document.getElementById('closeCart')?.addEventListener('click', closeCart);
    document.getElementById('cartOverlay')?.addEventListener('click', closeCart);
    document.getElementById('closeModal')?.addEventListener('click', closeModal);
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const cat = e.target.dataset.category;
            const filtered = cat === 'all' ? PRODUCTS : PRODUCTS.filter(p => p.category === cat);
            renderProducts(document.getElementById('productGrid'), filtered);
        });
    });
    document.getElementById('productSearch')?.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = PRODUCTS.filter(p => p.name.toLowerCase().includes(term) || p.category.toLowerCase().includes(term));
        renderProducts(document.getElementById('productGrid'), filtered);
    });
    window.addEventListener('scroll', () => {
        const nav = document.getElementById('mainNav');
        if (nav) {
            if (window.scrollY > 50) nav.classList.add('scrolled');
            else nav.classList.remove('scrolled');
        }
    });
}

window.openProduct = openProduct;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;

init();
