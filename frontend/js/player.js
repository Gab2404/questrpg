// Player Dashboard Logic - VERSION ORIGINALE (ne pas modifier)

// ⚔️ MAP DES EMOJIS POUR L'AFFICHAGE
const ITEM_ICONS = {
    "Épée": "⚔️",
    "Bouclier": "🛡️",
    "Potion": "🧪",
    "Parchemin": "📜",
    "Coupe": "🏆"
};

async function loadPlayerStatus() {
    try {
        const status = await api.getPlayerStatus();
        console.log('📊 Player Status:', status);
        displayPlayerStatus(status);
    } catch (error) {
        notify.error('Erreur lors du chargement du statut');
        console.error(error);
    }
}

function displayPlayerStatus(status) {
    document.getElementById('playerName').textContent = status.name;
    document.getElementById('playerLevel').textContent = status.level;
    document.getElementById('playerXP').textContent = status.xp;
    document.getElementById('playerMoney').textContent = status.money;
    document.getElementById('completedQuestsCount').textContent = status.completed_quests.length;

    // Inventory avec Emojis
    const inventoryContainer = document.getElementById('inventory');
    if (status.inventory.length === 0) {
        inventoryContainer.innerHTML = '<p style="text-align:center; color:#999;">Inventaire vide</p>';
    } else {
        inventoryContainer.innerHTML = status.inventory.map(item => {
            // Cherche l'emoji, sinon met un sac par défaut
            const icon = ITEM_ICONS[item] || '🎒';
            return `
            <div class="inventory-item">
                <div style="font-size: 2rem;">${icon}</div>
                <div>${item}</div>
            </div>
            `;
        }).join('');
    }

    // NPC Status
    const npcBtn = document.getElementById('talkNPCBtn');
    if (status.spoken_to_npc) {
        npcBtn.textContent = '✓ PNJ contacté';
        npcBtn.classList.add('btn-success');
        npcBtn.classList.remove('btn-primary');
    }
}

async function loadQuests() {
    try {
        const quests = await api.getQuests();
        console.log('🎯 Quests received:', quests);
        
        quests.forEach(q => {
            console.log(`Quest #${q.id} "${q.title}":`, {
                is_completed: q.is_completed,
                can_start: q.can_start,
                decorators: q.decorators,
                missing: q.missing_requirements
            });
        });
        
        displayQuests(quests);
    } catch (error) {
        notify.error('Erreur lors du chargement des quêtes');
        console.error(error);
    }
}

function displayQuests(quests) {
    const container = document.getElementById('questsList');
    
    if (quests.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#999;">Aucune quête disponible</p>';
        return;
    }

    container.innerHTML = quests.map(quest => {
        let debugInfo = '';
        if (window.location.search.includes('debug=1')) {
            debugInfo = `
                <div style="background: #f0f0f0; padding: 0.5rem; margin-top: 0.5rem; font-size: 0.75rem; font-family: monospace;">
                    DEBUG: is_completed=${quest.is_completed}, can_start=${quest.can_start}
                </div>
            `;
        }
        
        const statusBadge = quest.is_completed 
            ? '<span class="badge badge-completed">✓ Terminée</span>'
            : quest.can_start
                ? '<span class="badge badge-available">Disponible</span>'
                : '<span class="badge badge-locked">🔒 Verrouillée</span>';
        
        const typeBadge = quest.type === 'PRIMARY'
            ? '<span class="badge badge-primary">Principale</span>'
            : '<span class="badge badge-secondary">Secondaire</span>';

        let requirementsHTML = '';
        if (quest.missing_requirements && quest.missing_requirements.length > 0) {
            requirementsHTML = `
                <div class="quest-requirements">
                    <strong>Conditions manquantes:</strong>
                    ${quest.missing_requirements.map(req => `
                        <div class="requirement unmet">✗ ${req}</div>
                    `).join('')}
                </div>
            `;
        }

        let rewardsHTML = '';
        const rewards = [];
        quest.decorators.forEach(dec => {
            if (dec.type === 'money_reward') rewards.push(`<span class="decorator-value">💰 ${dec.value} pièces</span>`);
            if (dec.type === 'item_reward') {
                 const icon = ITEM_ICONS[dec.value] || '🎁';
                 rewards.push(`<span class="decorator-value">${icon} ${dec.value}</span>`);
            }
        });
        if (rewards.length > 0) {
            rewardsHTML = `
                <div class="quest-rewards">
                    ${rewards.join('')}
                </div>
            `;
        }

        return `
            <div class="quest-item ${quest.is_completed ? 'completed' : quest.can_start ? '' : 'locked'}">
                <div class="quest-header">
                    <div>
                        <div class="quest-title">${quest.title}</div>
                        <div class="quest-meta">
                            ${typeBadge}
                            <span>⭐ ${quest.base_xp} XP</span>
                        </div>
                    </div>
                    ${statusBadge}
                </div>
                <div class="quest-description">${quest.description}</div>
                ${requirementsHTML}
                ${rewardsHTML}
                ${debugInfo}
                ${!quest.is_completed && quest.can_start ? `
                    <button class="btn btn-success mt-1" onclick="attemptQuest(${quest.id}, '${quest.title}')">
                        Accomplir cette quête
                    </button>
                ` : ''}
            </div>
        `;
    }).join('');
}

async function attemptQuest(questId, questTitle) {
    console.log(`🎮 Attempting quest #${questId}: "${questTitle}"`);
    
    try {
        const result = await api.completeQuest(questId);
        console.log('✅ Quest result:', result);
        
        if (result.success) {
            showQuestCompleteAnimation(questTitle, result.rewards);
            await Promise.all([loadPlayerStatus(), loadQuests()]);
        } else {
            notify.warning(result.message);
        }
    } catch (error) {
        notify.error('Erreur lors de la tentative de complétion');
        console.error('❌ Error:', error);
    }
}

function showQuestCompleteAnimation(questTitle, rewards) {
    const overlay = document.createElement('div');
    overlay.className = 'quest-complete-overlay';
    
    const rewardsHTML = [];
    if (rewards.xp) rewardsHTML.push(`<div class="reward-item">⭐ +${rewards.xp} XP</div>`);
    if (rewards.money) rewardsHTML.push(`<div class="reward-item">💰 +${rewards.money} pièces</div>`);
    
    // Affichage des objets avec icônes
    if (rewards.items) {
        rewards.items.forEach(item => {
             const icon = ITEM_ICONS[item] || '🎁';
            rewardsHTML.push(`<div class="reward-item">${icon} ${item}</div>`);
        });
    }
    if (rewards.leveled_up) {
        rewardsHTML.push(`<div class="reward-item level-up-badge">🎉 LEVEL UP! Niveau ${rewards.new_level}</div>`);
    }
    
    overlay.innerHTML = `
        <div class="quest-complete-card">
            <div class="quest-complete-icon">🎊</div>
            <div class="quest-complete-title">Quête terminée !</div>
            <h3>${questTitle}</h3>
            <div class="quest-complete-rewards">
                <strong>Récompenses obtenues:</strong>
                ${rewardsHTML.join('')}
            </div>
            <button class="btn btn-primary" onclick="this.closest('.quest-complete-overlay').remove()">
                Continuer
            </button>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    setTimeout(() => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });
    }, 100);
}

async function talkToNPC() {
    try {
        const result = await api.talkToNPC();
        console.log('💬 Talk to NPC result:', result);
        
        if (result.success) {
            notify.success(result.message);
            await Promise.all([loadPlayerStatus(), loadQuests()]);
        } else {
            notify.info(result.message);
        }
    } catch (error) {
        notify.error('Erreur lors de l\'interaction avec le PNJ');
        console.error(error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    if (!auth.requireAuth()) return;
    
    console.log('🎮 Player Dashboard Loading...');
    
    await loadPlayerStatus();
    await loadQuests();
    
    const talkNPCBtn = document.getElementById('talkNPCBtn');
    if (talkNPCBtn) {
        talkNPCBtn.addEventListener('click', talkToNPC);
    }
    
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            await Promise.all([loadPlayerStatus(), loadQuests()]);
            notify.success('Données actualisées');
        });
    }
    
    console.log('✅ Player Dashboard Ready');
});