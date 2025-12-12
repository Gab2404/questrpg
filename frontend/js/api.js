const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            // ✅ CORRECTION : Gérer les réponses sans body (204 No Content)
            if (response.status === 204) {
                return { success: true };
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erreur réseau');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    async register(username, password, isAdmin = false) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                username,
                password,
                is_admin: isAdmin
            })
        });

        this.setToken(data.access_token);
        return data;
    }

    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                username,
                password
            })
        });

        this.setToken(data.access_token);
        return data;
    }

    // Player
    async getPlayerStatus() {
        return await this.request('/player/status');
    }

    async getQuests() {
        return await this.request('/player/quests');
    }

    async completeQuest(questId) {
        return await this.request(`/player/quests/${questId}/complete`, {
            method: 'POST'
        });
    }

    async talkToNPC() {
        return await this.request('/player/talk-npc', {
            method: 'POST'
        });
    }

    // Admin
    async getAllQuests() {
        return await this.request('/admin/quests');
    }

    async createQuest(questData) {
        return await this.request('/admin/quests', {
            method: 'POST',
            body: JSON.stringify(questData)
        });
    }

    async updateQuest(questId, questData) {
        return await this.request(`/admin/quests/${questId}`, {
            method: 'PUT',
            body: JSON.stringify(questData)
        });
    }

    async deleteQuest(questId) {
        return await this.request(`/admin/quests/${questId}`, {
            method: 'DELETE'
        });
    }

    async fixQuestIds() {
        return await this.request('/admin/quests/fix-ids', {
            method: 'POST'
        });
    }

    async getAdminStats() {
        return await this.request('/admin/stats');
    }
}

const api = new APIClient();