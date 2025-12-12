/**
 * Formatte un nombre avec des espaces pour les milliers
 * @param {number} num - Le nombre à formater
 * @returns {string} - Nombre formaté
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

/**
 * Formatte une date
 * @param {Date|string} date - Date à formater
 * @returns {string} - Date formatée
 */
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('fr-FR', options);
}

/**
 * Capitalise la première lettre d'une chaîne
 * @param {string} str - Chaîne à capitaliser
 * @returns {string} - Chaîne capitalisée
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Tronque un texte à une longueur donnée
 * @param {string} text - Texte à tronquer
 * @param {number} maxLength - Longueur maximale
 * @returns {string} - Texte tronqué avec "..."
 */
function truncate(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Débounce une fonction
 * @param {Function} func - Fonction à débouncer
 * @param {number} delay - Délai en ms
 * @returns {Function} - Fonction débouncée
 */
function debounce(func, delay = 300) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Valide un email
 * @param {string} email - Email à valider
 * @returns {boolean} - True si valide
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Génère un ID aléatoire
 * @returns {string} - ID unique
 */
function generateId() {
    return '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Affiche/Cache un élément avec transition
 * @param {HTMLElement} element - Élément à animer
 * @param {boolean} show - True pour afficher, False pour cacher
 */
function toggleElement(element, show) {
    if (show) {
        element.classList.remove('hidden');
        element.classList.add('fade-enter');
        setTimeout(() => {
            element.classList.remove('fade-enter');
            element.classList.add('fade-enter-active');
        }, 10);
    } else {
        element.classList.add('fade-exit');
        setTimeout(() => {
            element.classList.add('hidden');
            element.classList.remove('fade-exit');
        }, 300);
    }
}

/**
 * Scroll smooth vers un élément
 * @param {string} selector - Sélecteur CSS de l'élément
 */
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Copie du texte dans le presse-papiers
 * @param {string} text - Texte à copier
 * @returns {Promise<boolean>} - True si succès
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Erreur de copie:', err);
        return false;
    }
}

/**
 * Obtient un paramètre de l'URL
 * @param {string} param - Nom du paramètre
 * @returns {string|null} - Valeur ou null
 */
function getUrlParameter(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Convertit un objet en query string
 * @param {Object} params - Paramètres
 * @returns {string} - Query string
 */
function objectToQueryString(params) {
    return Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
}

/**
 * Sauvegarde des données dans le localStorage de manière sécurisée
 * @param {string} key - Clé
 * @param {any} value - Valeur (sera stringifiée)
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (err) {
        console.error('Erreur de sauvegarde:', err);
    }
}

/**
 * Récupère des données du localStorage
 * @param {string} key - Clé
 * @returns {any|null} - Valeur parsée ou null
 */
function loadFromStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (err) {
        console.error('Erreur de chargement:', err);
        return null;
    }
}

/**
 * Convertit les secondes en format lisible (ex: "2h 30m")
 * @param {number} seconds - Secondes
 * @returns {string} - Format lisible
 */
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    const parts = [];
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);
    
    return parts.join(' ');
}

/**
 * Calcule le pourcentage
 * @param {number} value - Valeur actuelle
 * @param {number} max - Valeur maximale
 * @returns {number} - Pourcentage (0-100)
 */
function calculatePercentage(value, max) {
    if (max === 0) return 0;
    return Math.min(100, Math.max(0, (value / max) * 100));
}

// Export pour usage global
window.Utils = {
    formatNumber,
    formatDate,
    capitalize,
    truncate,
    debounce,
    isValidEmail,
    generateId,
    toggleElement,
    scrollToElement,
    copyToClipboard,
    getUrlParameter,
    objectToQueryString,
    saveToStorage,
    loadFromStorage,
    formatDuration,
    calculatePercentage
};