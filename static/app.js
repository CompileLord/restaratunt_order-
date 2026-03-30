const API_BASE = '/api/v1';

const app = {
    state: {
        token: localStorage.getItem('access_token') || null,
        user: null,
        products: [],
        categories: [],
        cart: [],
        currentCategory: null,
        searchQuery: ''
    },

    // -------------------------------------------------------------------------
    // INIT & ROUTING
    // -------------------------------------------------------------------------
    init: async function() {
        this.setupListeners();
        
        if (this.state.token) {
            await this.api.fetchUser();
        }

        if (this.state.user) {
            this.navigate('catalog');
        } else {
            this.navigate('login');
        }
    },

    navigate: function(view, params = {}) {
        const appContainer = document.getElementById('app');
        const navbar = document.getElementById('navbar');
        
        // Clear current content
        appContainer.innerHTML = '';
        
        // Setup Header visibility
        if (['login', 'register'].includes(view)) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
            this.updateNavbar();
        }

        window.scrollTo(0, 0);

        // Render appropriate view
        switch(view) {
            case 'login':
                this.renderLogin();
                break;
            case 'register':
                this.renderRegister();
                break;
            case 'catalog':
                this.renderCatalog();
                break;
            case 'cart':
                this.renderCart();
                break;
            case 'product':
                this.renderProduct(params.id);
                break;
            case 'orders':
                this.renderOrders();
                break;
            case 'admin_dashboard':
                this.renderAdminDashboard();
                break;
            default:
                this.renderCatalog();
        }
    },

    updateNavbar: function() {
        const navLinks = document.getElementById('navLinks');
        if (!this.state.user) return;
        
        navLinks.innerHTML = `
            <a href="#" onclick="app.navigate('catalog')" class="text-on-surface font-medium hover:opacity-80 transition-opacity font-headline text-sm">Explore</a>
            <a href="#" onclick="app.navigate('orders')" class="text-on-surface font-medium hover:opacity-80 transition-opacity font-headline text-sm">Orders</a>
        `;
        if (this.state.user.role === 'admin') {
            navLinks.innerHTML += `
                <a href="#" onclick="app.navigate('admin_dashboard')" class="text-primary font-bold border-b-2 border-primary font-headline text-sm ml-4">Admin Dashboard</a>
            `;
        }
        
        const badge = document.getElementById('cartCountBadge');
        const totalItems = this.state.cart.reduce((sum, item) => sum + item.quantity, 0);
        
        if (totalItems > 0) {
            badge.innerText = totalItems;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    },

    // -------------------------------------------------------------------------
    // API CLIENT
    // -------------------------------------------------------------------------
    api: {
        headers: function(includeContent = true) {
            const h = {};
            if (includeContent) h['Content-Type'] = 'application/json';
            if (app.state.token) h['Authorization'] = `Bearer ${app.state.token}`;
            return h;
        },

        fetchUser: async function() {
            try {
                const res = await fetch(`${API_BASE}/me`, { headers: this.headers() });
                if (res.ok) {
                    app.state.user = await res.json();
                } else {
                    app.logout();
                }
            } catch(e) {
                app.logout();
            }
        },

        login: async function(email, password) {
            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Login failed");
            
            localStorage.setItem('access_token', data.access_token);
            app.state.token = data.access_token;
            await this.fetchUser();
        },

        register: async function(data) {
            const res = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: this.headers(),
                body: JSON.stringify(data)
            });
            const json = await res.json();
            if (!res.ok) throw new Error(json.detail || "Registration failed");
            return json;
        },

        getProducts: async function(categoryId = null, search = '') {
            let url = `${API_BASE}/products/?limit=100`;
            if (categoryId) url += `&category_id=${categoryId}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            
            const res = await fetch(url, { headers: this.headers() });
            if (res.ok) {
                app.state.products = await res.json();
            }
        },

        getCategories: async function() {
            const res = await fetch(`${API_BASE}/get_all_categories`, { headers: this.headers() });
            if (res.ok) {
                app.state.categories = await res.json();
            }
        },

        getCart: async function() {
            const res = await fetch(`${API_BASE}/cart/`, { headers: this.headers() });
            if (res.ok) {
                app.state.cart = await res.json();
                app.updateNavbar();
            }
        },

        addToCart: async function(productId, quantity) {
            const res = await fetch(`${API_BASE}/cart/`, {
                method: 'POST',
                headers: this.headers(),
                body: JSON.stringify({ product_id: productId, quantity })
            });
            if (res.ok) {
                await this.getCart();
                app.showToast(quantity > 0 ? "Added to Cart!" : "Removed from Cart!", "success");
            } else {
                app.showToast("Failed to update cart.", "error");
            }
        },

        createOrder: async function(paymentMethod, address) {
            const res = await fetch(`${API_BASE}/orders/`, {
                method: 'POST',
                headers: this.headers(),
                body: JSON.stringify({ payment_method: paymentMethod, delivery_address: address })
            });
            if (!res.ok) throw new Error("Checkout failed");
            return await res.json();
        },

        getOrders: async function() {
            const res = await fetch(app.state.user.role === 'admin' ? `${API_BASE}/admin/orders` : `${API_BASE}/orders/`, { headers: this.headers() });
            if (res.ok) return await res.json();
            return [];
        },

        updateOrderStatus: async function(id, status) {
            const res = await fetch(`${API_BASE}/admin/orders/${id}`, {
                method: 'PATCH',
                headers: this.headers(),
                body: JSON.stringify({ status })
            });
            return res.ok;
        },

        addProduct: async function(formData) {
            const res = await fetch(`${API_BASE}/products/`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${app.state.token}` },
                body: formData
            });
            if (!res.ok) throw new Error("Adding product failed");
            return await res.json();
        },

        addCategory: async function(queryStr, formData) {
            const res = await fetch(`${API_BASE}/add_category?${queryStr}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${app.state.token}` },
                body: formData
            });
            if (!res.ok) throw new Error("Adding category failed");
            return await res.json();
        }
    },

    // -------------------------------------------------------------------------
    // UTILS
    // -------------------------------------------------------------------------
    logout: function() {
        localStorage.removeItem('access_token');
        this.state.token = null;
        this.state.user = null;
        this.navigate('login');
    },

    setupListeners: function() {
        const searchInput = document.getElementById('searchInput');
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.state.searchQuery = e.target.value;
                if(this.state.user) {
                    this.renderCatalog(false); // Re-render but keep it seamless
                }
            }, 500);
        });

        document.getElementById('profileBtn').addEventListener('click', () => {
             if(confirm('Do you want to logout?')) {
                 this.logout();
             }
        });
    },

    showToast: function(msg, type='info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `glass-panel px-6 py-3 rounded-full text-sm font-bold shadow-lg transform transition-all duration-300 translate-y-10 opacity-0 ${type === 'error' ? 'bg-error text-white' : 'bg-surface-variant/90 text-on-surface'}`;
        toast.innerText = msg;
        
        container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');
        });

        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // -------------------------------------------------------------------------
    // VIEWS
    // -------------------------------------------------------------------------
    renderLogin: function() {
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = `
        <div class="min-h-screen flex items-center justify-center px-6 page-transition">
            <div class="grid lg:grid-cols-2 max-w-6xl w-full gap-12 items-center">
                <div class="hidden lg:block relative rounded-[2rem] overflow-hidden aspect-[4/5] shadow-2xl">
                    <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuB9V9HAsipWSYvOhTWnY2EY3-YNHYp7E5dipvG9cMoZaj1Pfc760p8sJPP3fPwVt0jwBD3Mr_Hl9OWBxpZYSIt7r1FHkI9o9C3o68k8tx7vSLaZQeySc9U1CNvE_jbBK8Mf56KtfjqpiRN6_l0rDRgrGYDyqsFSLEJCH51bd23EVi3yYmTgmb_KzYlGknRXgfpG8aGon92Qb0jLgY-W0T56-33g4sVXZ7AejN8sR24CMoN6aauXB4fGG9PSjnp26er9RPOXGNVD1u8" class="absolute inset-0 w-full h-full object-cover">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-12">
                        <h2 class="font-headline text-white text-4xl font-bold mb-4 leading-tight">Your daily dose of curated flavors.</h2>
                    </div>
                </div>
                <!-- Login Form -->
                <div class="w-full max-w-md mx-auto">
                    <div class="mb-10">
                        <h1 class="font-headline text-3xl text-on-surface font-bold mb-3">Welcome back</h1>
                        <p class="text-on-surface-variant font-body">Sign in to continue your culinary journey.</p>
                    </div>
                    <form id="loginForm" class="space-y-6">
                        <div class="space-y-2">
                            <label class="block text-xs font-bold text-on-surface ml-1">Email</label>
                            <input type="email" id="loginEmail" class="w-full bg-surface-container-low border-none rounded-xl px-4 py-4 focus:ring-2 focus:ring-primary/30 outline-none" placeholder="name@example.com" required>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-xs font-bold text-on-surface ml-1">Password</label>
                            <input type="password" id="loginPassword" class="w-full bg-surface-container-low border-none rounded-xl px-4 py-4 focus:ring-2 focus:ring-primary/30 outline-none" placeholder="••••••••" required>
                        </div>
                        <button type="submit" id="loginBtn" class="w-full editorial-gradient text-on-primary font-bold py-4 rounded-xl shadow-lg active:scale-95 transition-all">
                            Log In
                        </button>
                    </form>
                    <div class="mt-12 text-center text-sm">
                        Don't have an account? <a href="#" onclick="app.navigate('register')" class="text-primary font-bold hover:underline">Sign Up</a>
                    </div>
                </div>
            </div>
        </div>`;

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            btn.innerHTML = '<div class="loader mx-auto"></div>';
            try {
                await this.api.login(document.getElementById('loginEmail').value, document.getElementById('loginPassword').value);
                this.navigate('catalog');
            } catch(err) {
                this.showToast(err.message, 'error');
                btn.innerText = 'Log In';
            }
        });
    },

    renderRegister: function() {
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = `
        <div class="min-h-screen flex items-center justify-center px-6 page-transition">
            <div class="w-full max-w-md mx-auto">
                <div class="mb-10 text-center">
                    <h1 class="font-headline text-3xl text-on-surface font-bold mb-3">Join the Club</h1>
                    <p class="text-on-surface-variant font-body">Create your account to start ordering.</p>
                </div>
                <form id="regForm" class="space-y-4">
                    <div class="space-y-1">
                        <label class="block text-xs font-bold text-on-surface ml-1">Full Name</label>
                        <input type="text" id="regName" class="w-full bg-surface-container-low border-none rounded-xl px-4 py-3 outline-none" required>
                    </div>
                    <div class="space-y-1">
                        <label class="block text-xs font-bold text-on-surface ml-1">Email</label>
                        <input type="email" id="regEmail" class="w-full bg-surface-container-low border-none rounded-xl px-4 py-3 outline-none" required>
                    </div>
                    <div class="space-y-1">
                        <label class="block text-xs font-bold text-on-surface ml-1">Phone</label>
                        <input type="text" id="regPhone" class="w-full bg-surface-container-low border-none rounded-xl px-4 py-3 outline-none" required>
                    </div>
                    <div class="space-y-1">
                        <label class="block text-xs font-bold text-on-surface ml-1">Password</label>
                        <input type="password" id="regPass" class="w-full bg-surface-container-low border-none rounded-xl px-4 py-3 outline-none" required>
                    </div>
                    <button type="submit" id="regBtn" class="w-full editorial-gradient text-on-primary font-bold py-4 rounded-xl shadow-lg mt-6">
                        Sign Up
                    </button>
                </form>
                <div class="mt-8 text-center text-sm">
                    Already have an account? <a href="#" onclick="app.navigate('login')" class="text-primary font-bold hover:underline">Log In</a>
                </div>
            </div>
        </div>`;

        document.getElementById('regForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('regBtn');
            btn.innerHTML = '<div class="loader mx-auto"></div>';
            try {
                await this.api.register({
                    full_name: document.getElementById('regName').value,
                    email: document.getElementById('regEmail').value,
                    phone: document.getElementById('regPhone').value,
                    password: document.getElementById('regPass').value,
                });
                this.showToast("Registration successful! Please login.");
                this.navigate('login');
            } catch(err) {
                this.showToast(err.message, 'error');
                btn.innerText = 'Sign Up';
            }
        });
    },

    renderCatalog: async function(fullRender = true) {
        if (!this.state.user) return this.navigate('login');
        
        let appContainer = document.getElementById('app');
        
        if (fullRender) {
            appContainer.innerHTML = `
            <main class="pt-24 pb-12 max-w-7xl mx-auto px-6 page-transition">
                <!-- Hero section -->
                <section class="mb-12">
                    <div class="relative h-[300px] w-full rounded-3xl overflow-hidden bg-surface-container-highest">
                        <img class="w-full h-full object-cover opacity-90" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCcXtSSCBIWeR6yz5GXTdZvffsOq7bKNlM9DQcDnXVK9wSQl7C9rmPXz8xzHcsCf2EWaCSQ9ekfVF2uSfz2M4Y1D0FIBaBvmpaKPpACA3rIvY7iGDyArLsfCDhdpiw4__mXhLB4S6GvzrWa9jmIkwEJ9lx4-0-Z1uULwADV-YuvaMAK37lmuQKKrOHx_TLr5lDe1lMx8z_ZVzX_H5CbCv8Id8JDZcOZcUZb91YAf-f1jnpx5uu2sg8CIGo23wYm4QrR-aOKU5yG1y4">
                        <div class="absolute inset-0 bg-gradient-to-r from-on-surface/80 to-transparent flex flex-col justify-center px-12 text-white">
                            <h1 class="font-headline text-5xl font-extrabold mb-2 tracking-tight">Gourmet Discoveries</h1>
                            <p class="max-w-md text-surface-variant font-medium">Every dish is a handpicked masterpiece.</p>
                        </div>
                    </div>
                </section>
                
                <!-- Category Pills -->
                <section class="mb-10 space-y-6">
                    <div id="categoryContainer" class="flex items-center gap-4 overflow-x-auto hide-scrollbar pb-2">
                         <div class="loader"></div>
                    </div>
                </section>

                <!-- Product Grid -->
                <section id="productGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                    <div class="loader"></div>
                </section>
            </main>`;

            await Promise.all([
                this.api.getCategories(),
                this.api.getCart()
            ]);
            
            // Render categories
            const catContainer = document.getElementById('categoryContainer');
            let catHtml = `<button onclick="app.setCategory(null)" class="${this.state.currentCategory === null ? 'bg-primary-container text-on-primary-container' : 'bg-surface-container-high text-on-surface'} font-label text-xs font-bold px-6 py-3 rounded-full whitespace-nowrap active:scale-95 transition-all">All Cuisines</button>`;
            
            this.state.categories.forEach(c => {
                const isActive = this.state.currentCategory === c.id;
                catHtml += `<button onclick="app.setCategory(${c.id})" class="${isActive ? 'bg-primary-container text-on-primary-container' : 'bg-surface-container-high text-on-surface hover:bg-surface-container-highest'} font-label text-xs font-semibold px-6 py-3 rounded-full whitespace-nowrap active:scale-95 transition-all">${c.title}</button>`;
            });
            catContainer.innerHTML = catHtml;
        }

        // Fetch & render products
        const grid = document.getElementById('productGrid');
        await this.api.getProducts(this.state.currentCategory, this.state.searchQuery);
        
        if (this.state.products.length === 0) {
            grid.innerHTML = `<div class="col-span-full py-12 text-center text-on-surface-variant">No products found.</div>`;
            return;
        }

        let productsHtml = '';
        this.state.products.forEach(p => {
            const imgUrl = p.image_url ? (p.image_url.startsWith('http') ? p.image_url : `/${p.image_url}`) : 'https://placehold.co/400x500/eaeaea/a63300?text=No+Image';
            
            productsHtml += `
            <div class="group bg-surface-container-lowest rounded-[2rem] overflow-hidden transition-all duration-300 hover:shadow-[0_24px_48px_-12px_rgba(45,47,47,0.1)] hover:-translate-y-1">
                <div class="relative aspect-[4/5] overflow-hidden cursor-pointer" onclick="app.navigate('product', {id: ${p.id}})">
                    <img class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" src="${imgUrl}">
                </div>
                <div class="p-6 flex flex-col h-40">
                    <h3 class="font-headline text-lg font-bold text-on-surface mb-1">${p.title}</h3>
                    <p class="text-on-surface-variant text-xs line-clamp-2">${p.description}</p>
                    <div class="flex items-center justify-between mt-auto">
                        <span class="text-primary font-bold text-lg">$${p.price.toFixed(2)}</span>
                        <button onclick="app.api.addToCart(${p.id}, 1)" class="bg-primary hover:bg-primary-dim text-white flex items-center gap-2 px-5 py-2.5 rounded-xl font-label text-xs transition-all active:scale-95 shadow-md">
                            <span class="material-symbols-outlined text-sm">add</span> Add
                        </button>
                    </div>
                </div>
            </div>`;
        });
        grid.innerHTML = productsHtml;
    },

    setCategory: function(id) {
        this.state.currentCategory = id;
        this.renderCatalog(true);
    },

    renderCart: async function() {
        if (!this.state.user) return this.navigate('login');
        
        await this.api.getCart();
        const appContainer = document.getElementById('app');
        
        let cartHtml = `
        <main class="pt-24 pb-12 max-w-4xl mx-auto px-6 page-transition">
            <div class="flex items-center justify-between mb-8">
                <h1 class="font-headline text-3xl font-bold text-on-surface">Your Order</h1>
                <button onclick="app.navigate('catalog')" class="text-on-surface-variant font-bold text-sm hover:text-primary transition-colors">Continue Browsing</button>
            </div>
            
            <div class="bg-surface-container-lowest rounded-3xl p-8 shadow-sm">
        `;

        if (this.state.cart.length === 0) {
            cartHtml += `<div class="text-center py-12 text-on-surface-variant font-medium text-lg">Your cart is empty.</div>`;
        } else {
            let total = 0;
            this.state.cart.forEach(item => {
                total += item.quantity * item.product.price;
                cartHtml += `
                <div class="flex items-center justify-between border-b border-surface-container py-4 last:border-0">
                    <div class="flex items-center gap-4">
                            <div class="w-16 h-16 rounded-xl overflow-hidden bg-surface-container">
                                 <img src="${item.product.image_url ? (item.product.image_url.startsWith('http') ? item.product.image_url : '/'+item.product.image_url) : 'https://placehold.co/150x150/eaeaea/a63300?text=No+Image'}" class="w-full h-full object-cover">
                            </div>
                        <div>
                            <h3 class="font-bold text-on-surface">${item.product.title}</h3>
                            <span class="text-sm text-primary font-bold">$${item.product.price.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="text-sm font-bold text-on-surface px-3 bg-surface-container-low rounded-lg py-1">Qty: ${item.quantity}</span>
                        <button onclick="app.api.addToCart(${item.product.id}, -1)" class="text-error hover:opacity-80"><span class="material-symbols-outlined text-lg">delete</span></button>
                    </div>
                </div>
                `;
            });
            
            cartHtml += `
                <div class="mt-8 pt-8 border-t border-surface-container flex justify-between items-center">
                    <span class="text-xl font-headline font-bold text-on-surface">Total: $${total.toFixed(2)}</span>
                    <button onclick="app.checkoutOrder()" class="editorial-gradient text-white px-8 py-3 rounded-xl font-bold shadow-lg active:scale-95 transition-all">Checkout</button>
                </div>
            `;
        }

        cartHtml += `</div></main>`;
        appContainer.innerHTML = cartHtml;
    },

    checkoutOrder: async function() {
        // Create modal container
        const modal = document.createElement('div');
        modal.className = "fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm opacity-0 transition-opacity duration-300";
        modal.innerHTML = `
            <div class="bg-surface-container-lowest rounded-3xl p-8 shadow-2xl w-full max-w-md transform scale-95 transition-transform duration-300">
                <h2 class="font-headline text-2xl font-bold text-on-surface mb-2">Checkout</h2>
                <p class="text-on-surface-variant mb-6 text-sm">Please provide your delivery details below.</p>
                <form id="checkoutForm" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-on-surface mb-1">Delivery Address</label>
                        <input type="text" id="checkoutAddress" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-primary/50" placeholder="123 Main St" required>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-on-surface mb-1">Payment Method</label>
                        <select id="checkoutPayment" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-primary/50" required>
                            <option value="cash" selected>Cash on Delivery</option>
                            <option value="card">Credit/Debit Card</option>
                        </select>
                    </div>
                    <div class="flex gap-4 mt-8">
                        <button type="button" id="closeCheckoutBtn" class="flex-1 px-4 py-3 rounded-xl font-bold text-on-surface hover:bg-surface-container transition-colors">Cancel</button>
                        <button type="submit" class="flex-1 bg-primary text-white px-4 py-3 rounded-xl font-bold hover:opacity-90 transition-opacity shadow-lg">Confirm</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Animate in
        requestAnimationFrame(() => {
            modal.classList.remove('opacity-0');
            modal.querySelector('div').classList.remove('scale-95');
        });

        const closeModal = () => {
            modal.classList.add('opacity-0');
            modal.querySelector('div').classList.add('scale-95');
            setTimeout(() => modal.remove(), 300);
        };

        modal.querySelector('#closeCheckoutBtn').addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        modal.querySelector('#checkoutForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const address = document.getElementById('checkoutAddress').value;
            const paymentMethod = document.getElementById('checkoutPayment').value;
            const submitBtn = e.target.querySelector('button[type="submit"]');
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="loader mx-auto h-5 w-5 border-2"></div>';
            
            try {
                await this.api.createOrder(paymentMethod, address);
                closeModal();
                this.showToast("Order placed successfully!", "success");
                this.state.cart = [];
                this.updateNavbar();
                this.navigate('orders');
            } catch(err) {
                this.showToast(err.message, "error");
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Confirm';
            }
        });
    },

    renderProduct: async function(id) {
        if (!this.state.user) return this.navigate('login');
        const res = await fetch(`${API_BASE}/products/${id}`, { headers: this.api.headers() });
        const product = await res.json();
        const imgUrl = product.image_url ? (product.image_url.startsWith('http') ? product.image_url : `/${product.image_url}`) : 'https://placehold.co/800x600/eaeaea/a63300?text=No+Image';
        
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = `
        <main class="pt-24 pb-12 max-w-6xl mx-auto px-6 page-transition">
            <button onclick="app.navigate('catalog')" class="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors font-bold text-sm mb-8 active:scale-95">
                <span class="material-symbols-outlined text-lg">arrow_back</span> Back to Catalog
            </button>
            <div class="grid lg:grid-cols-2 gap-12">
                <div class="rounded-[2.5rem] overflow-hidden bg-surface-container shadow-lg aspect-square">
                    <img src="${imgUrl}" class="w-full h-full object-cover">
                </div>
                <div class="flex flex-col justify-center">
                    <span class="bg-primary-container/20 text-primary text-xs font-bold px-3 py-1 rounded-full w-fit mb-4">Gourmet Selection</span>
                    <h1 class="font-headline text-4xl font-extrabold text-on-surface mb-2">${product.title}</h1>
                    <p class="text-on-surface-variant mb-8">${product.description}</p>
                    
                    ${product.ingredients ? `
                    <div class="mb-8">
                        <h3 class="font-bold text-sm text-on-surface mb-2 tracking-wide uppercase">Ingredients</h3>
                        <p class="text-on-surface-variant text-sm">${product.ingredients}</p>
                    </div>` : ''}
                    
                    <div class="flex items-center justify-between mb-8 p-6 bg-surface-container-low rounded-3xl">
                        <span class="text-3xl font-headline font-extrabold text-primary">$${product.price.toFixed(2)}</span>
                        ${product.discount_percent ? `<span class="bg-error text-white text-xs font-bold px-3 py-1 rounded-full">-${product.discount_percent}%</span>` : ''}
                    </div>
                    
                    <div class="flex items-center gap-6 mb-8">
                        <div class="flex items-center bg-surface-container-low rounded-2xl overflow-hidden p-1 shadow-sm">
                            <button onclick="const el=document.getElementById('productQty'); el.value=Math.max(1, parseInt(el.value)-1)" class="w-12 h-12 flex items-center justify-center text-on-surface hover:bg-surface-container transition-colors rounded-xl material-symbols-outlined">remove</button>
                            <input type="number" id="productQty" value="1" min="1" class="w-16 h-12 text-center bg-transparent border-none outline-none font-bold text-lg text-on-surface">
                            <button onclick="const el=document.getElementById('productQty'); el.value=parseInt(el.value)+1" class="w-12 h-12 flex items-center justify-center text-on-surface hover:bg-surface-container transition-colors rounded-xl material-symbols-outlined">add</button>
                        </div>
                        <button onclick="app.api.addToCart(${product.id}, parseInt(document.getElementById('productQty').value))" class="flex-1 editorial-gradient text-white text-lg font-bold py-5 rounded-2xl shadow-xl active:scale-95 transition-all flex justify-center items-center gap-3 hover:shadow-2xl">
                            <span class="material-symbols-outlined">add_shopping_cart</span> Add to Order
                        </button>
                    </div>
                </div>
            </div>
        </main>`;
    },

    renderOrders: async function() {
        if (!this.state.user) return this.navigate('login');
        const orders = await this.api.getOrders();
        
        const appContainer = document.getElementById('app');
        let html = `
        <main class="pt-24 pb-12 max-w-4xl mx-auto px-6 page-transition">
            <h1 class="font-headline text-3xl font-bold text-on-surface mb-8">Your Orders</h1>
            <div class="space-y-6">
        `;
        
        if (orders.length === 0) {
            html += `<div class="bg-surface-container-lowest rounded-3xl p-8 text-center text-on-surface-variant shadow-sm">No orders found.</div>`;
        } else {
            orders.forEach(o => {
                html += `
                <div class="bg-surface-container-lowest rounded-3xl p-6 shadow-sm border border-surface-container flex flex-col sm:flex-row justify-between gap-6">
                    <div>
                        <div class="font-bold text-lg mb-1">Order #${o.id}</div>
                        <div class="text-sm text-on-surface-variant flex gap-4">
                            <span>Status: <span class="font-bold px-2 py-0.5 rounded-full ${o.status==='completed'?'bg-secondary-container text-on-secondary-container':'bg-surface-container-high'}">${o.status}</span></span>
                            <span>Total: <span class="font-bold text-primary">$${parseFloat(o.total_amount).toFixed(2)}</span></span>
                        </div>
                        <div class="text-xs text-on-surface-variant mt-2">Delivery: ${o.delivery_address}</div>
                    </div>
                </div>`;
            });
        }
        
        html += `</div></main>`;
        appContainer.innerHTML = html;
    },

    renderAdminDashboard: async function() {
        if (!this.state.user || this.state.user.role !== 'admin') return this.navigate('catalog');
        await this.api.getCategories();
        const orders = await this.api.getOrders();
        
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = `
        <main class="pt-24 pb-12 max-w-6xl mx-auto px-6 page-transition">
            <h1 class="font-headline text-3xl font-bold text-on-surface mb-8">Admin Dashboard</h1>
            
            <div class="grid lg:grid-cols-2 gap-8 mb-12">
                <!-- Add Category -->
                <div class="bg-surface-container-lowest rounded-[2rem] p-8 shadow-sm">
                    <h2 class="font-headline text-xl font-bold mb-6">Add Category</h2>
                    <form id="adminCatForm" class="space-y-4">
                        <input type="text" id="catTitle" placeholder="Title" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none border-none" required>
                        <input type="text" id="catDesc" placeholder="Description" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none border-none" required>
                        <div class="px-4 py-3 bg-surface-container-low rounded-xl">
                            <input type="file" id="catImage" class="w-full text-sm outline-none border-none" accept="image/*" required>
                        </div>
                        <button type="submit" class="w-full bg-primary text-white font-bold py-3 rounded-xl shadow-md mt-2 active:scale-95 transition-all">Add Category</button>
                    </form>
                </div>
                
                <!-- Add Product -->
                <div class="bg-surface-container-lowest rounded-[2rem] p-8 shadow-sm">
                    <h2 class="font-headline text-xl font-bold mb-6">Add Product</h2>
                    <form id="adminProdForm" class="space-y-4">
                        <input type="text" id="prodTitle" placeholder="Title" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none border-none" required>
                        <textarea id="prodDesc" placeholder="Description" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none border-none" required></textarea>
                        <div class="grid grid-cols-2 gap-4">
                            <input type="number" id="prodPrice" step="0.01" placeholder="Price" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none border-none" required>
                            <select id="prodCat" class="w-full bg-surface-container-low px-4 py-3 rounded-xl outline-none border-none" required>
                                <option value="">Category</option>
                                ${this.state.categories.map(c => `<option value="${c.id}">${c.title}</option>`).join('')}
                            </select>
                        </div>
                        <div class="px-4 py-3 bg-surface-container-low rounded-xl">
                            <input type="file" id="prodImage" class="w-full text-sm outline-none border-none" accept="image/*">
                        </div>
                        <button type="submit" class="w-full bg-primary text-white font-bold py-3 rounded-xl shadow-md mt-2 active:scale-95 transition-all">Add Product</button>
                    </form>
                </div>
            </div>

            <h2 class="font-headline text-2xl font-bold text-on-surface mb-6">Manage Orders</h2>
            <div class="space-y-4">
                ${orders.map(o => `
                <div class="bg-surface-container-lowest rounded-3xl p-6 shadow-sm border border-surface-container flex flex-wrap items-center justify-between gap-6">
                    <div>
                        <div class="font-bold text-lg mb-1">Order #${o.id} <span class="text-sm font-normal text-on-surface-variant ml-2">(User ${o.user_id})</span></div>
                        <div class="text-sm text-on-surface-variant flex gap-4">
                            <span>Total: <span class="font-bold text-primary">$${parseFloat(o.total_amount).toFixed(2)}</span></span>
                            <span>Delivery: ${o.delivery_address}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <select onchange="app.api.updateOrderStatus(${o.id}, this.value).then(()=>app.renderAdminDashboard())" class="bg-surface-container-low px-4 py-2 rounded-xl text-sm font-bold border-none outline-none">
                            ${['new', 'preparing', 'delivering', 'completed', 'cancelled'].map(s => 
                                `<option value="${s}" ${o.status === s ? 'selected' : ''}>${s.toUpperCase()}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
                `).join('')}
                ${orders.length === 0 ? '<div class="text-center py-12 text-on-surface-variant">No orders yet.</div>' : ''}
            </div>
        </main>`;

        document.getElementById('adminCatForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button'); btn.disabled = true;
            try {
                const formData = new FormData();
                formData.append('image', document.getElementById('catImage').files[0]);
                const params = new URLSearchParams({ title: document.getElementById('catTitle').value, description: document.getElementById('catDesc').value });
                await this.api.addCategory(params.toString(), formData);
                app.showToast("Category added", "success");
                e.target.reset();
            } catch(err) { app.showToast(err.message, "error"); }
            btn.disabled = false;
        });

        document.getElementById('adminProdForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button'); btn.disabled = true;
            try {
                const formData = new FormData();
                formData.append('title', document.getElementById('prodTitle').value);
                formData.append('description', document.getElementById('prodDesc').value);
                formData.append('price', document.getElementById('prodPrice').value);
                formData.append('category_id', document.getElementById('prodCat').value);
                if (document.getElementById('prodImage').files[0]) {
                    formData.append('image', document.getElementById('prodImage').files[0]);
                }
                await this.api.addProduct(formData);
                app.showToast("Product added", "success");
                e.target.reset();
            } catch(err) { app.showToast(err.message, "error"); }
            btn.disabled = false;
        });
    }
};

window.onload = () => app.init();
