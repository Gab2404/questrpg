class AuthManager {
    constructor() {
        this.currentUser = this.loadUser();
    }

    loadUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    saveUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
        this.currentUser = user;
    }

    isAuthenticated() {
        return this.currentUser !== null && api.token !== null;
    }

    isAdmin() {
        return this.currentUser && this.currentUser.is_admin;
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.currentUser = null;
        api.clearToken();
        window.location.href = 'login.html';
    }

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    requireAdmin() {
        if (!this.isAuthenticated() || !this.isAdmin()) {
            notify.error('Accès refusé. Droits administrateur requis.');
            window.location.href = 'player-dashboard.html';
            return false;
        }
        return true;
    }

    getUser() {
        return this.currentUser;
    }
}

const auth = new AuthManager();

// Handle login form
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const submitBtn = e.target.querySelector('button[type="submit"]');
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Connexion...';

        try {
            const data = await api.login(username, password);
            auth.saveUser(data.user);
            
            notify.success('Connexion réussie !');
            
            setTimeout(() => {
                if (data.user.is_admin) {
                    window.location.href = 'admin-dashboard.html';
                } else {
                    window.location.href = 'player-dashboard.html';
                }
            }, 500);
        } catch (error) {
            notify.error('Nom d\'utilisateur ou mot de passe incorrect');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Se connecter';
        }
    });
}

// Handle register form
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const isAdmin = document.getElementById('isAdmin')?.checked || false;
        const submitBtn = e.target.querySelector('button[type="submit"]');
        
        if (password !== confirmPassword) {
            notify.error('Les mots de passe ne correspondent pas');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Inscription...';

        try {
            const data = await api.register(username, password, isAdmin);
            auth.saveUser(data.user);
            
            notify.success('Inscription réussie !');
            
            setTimeout(() => {
                if (data.user.is_admin) {
                    window.location.href = 'admin-dashboard.html';
                } else {
                    window.location.href = 'player-dashboard.html';
                }
            }, 500);
        } catch (error) {
            notify.error(error.message || 'Erreur lors de l\'inscription');
            submitBtn.disabled = false;
            submitBtn.textContent = 'S\'inscrire';
        }
    });
}

// Logout button handler
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            auth.logout();
        });
    }
});