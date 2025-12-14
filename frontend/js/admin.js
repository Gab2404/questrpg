// Admin Dashboard Logic

let currentEditingQuest = null;

// ⚔️ NOUVEAU : Liste des objets pour le menu déroulant
const PREDEFINED_ITEMS = {
    "Épée": "⚔️",
    "Bouclier": "🛡️",
    "Potion": "🧪",
    "Parchemin": "📜",
    "Coupe": "🏆"
};

async function loadAdminQuests() {
    try {
        const quests = await api.getAllQuests();
        displayAdminQuests(quests);
    } catch (error) {
        notify.error('Erreur lors du chargement des quêtes');
        console.error(error);
    }
}

function displayAdminQuests(quests) {
    const tbody = document.getElementById('questsTableBody');
    
    if (quests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#999;">Aucune quête créée</td></tr>';
        return;
    }

    tbody.innerHTML = '';  // Vider d'abord
    
    quests.forEach(quest => {
        const typeLabel = quest.type === 'PRIMARY' ? 'Principale' : 'Secondaire';
        const badgeClass = quest.type === 'PRIMARY' ? 'badge-primary' : 'badge-success';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${quest.id}</td>
            <td>${quest.title}</td>
            <td><span class="badge ${badgeClass}">${typeLabel}</span></td>
            <td>${quest.base_xp} XP</td>
            <td>${quest.decorators.length}</td>
            <td>
                <button class="btn-icon btn-edit" data-id="${quest.id}" title="Modifier">✏️</button>
                <button class="btn-icon btn-delete" data-id="${quest.id}" data-title="${quest.title}" title="Supprimer">🗑️</button>
            </td>
        `;
        
        // Attacher les événements directement
        const editBtn = row.querySelector('.btn-edit');
        const deleteBtn = row.querySelector('.btn-delete');
        
        editBtn.addEventListener('click', () => {
            console.log('Edit clicked for quest', quest.id);
            editQuest(quest.id);
        });
        
        deleteBtn.addEventListener('click', () => {
            console.log('Delete clicked for quest', quest.id, quest.title);
            deleteQuest(quest.id, quest.title);
        });
        
        tbody.appendChild(row);
    });
}

async function loadAdminStats() {
    try {
        const stats = await api.getAdminStats();
        document.getElementById('totalUsers').textContent = stats.total_users;
        document.getElementById('totalQuests').textContent = stats.total_quests;
        
        // Afficher les stats "Terminées" et "En cours" si disponibles
        if (stats.total_completed !== undefined) {
            document.getElementById('totalCompleted').textContent = stats.total_completed;
        } else {
            document.getElementById('totalCompleted').textContent = '0';
        }
        
        if (stats.total_in_progress !== undefined) {
            document.getElementById('totalInProgress').textContent = stats.total_in_progress;
        } else {
            document.getElementById('totalInProgress').textContent = '0';
        }
    } catch (error) {
        console.error('Erreur stats:', error);
        // Valeurs par défaut en cas d'erreur
        document.getElementById('totalCompleted').textContent = '0';
        document.getElementById('totalInProgress').textContent = '0';
    }
}

function showCreateQuestModal() {
    document.getElementById('modalTitle').textContent = 'Créer une nouvelle quête';
    document.getElementById('questForm').reset();
    document.getElementById('decoratorsList').innerHTML = '<p style="color:#999;">Aucun décorateur configuré</p>';
    document.getElementById('decoratorsData').value = '[]';
    
    const addDecForm = document.getElementById('addDecoratorForm');
    addDecForm.classList.add('hidden');
    // On s'assure que le champ est bien un input text par défaut
    updateDecoratorValueField();
    document.getElementById('decoratorValue').removeAttribute('required');
    
    currentEditingQuest = null;
    document.getElementById('questModal').classList.add('active');
}

async function editQuest(questId) {
    try {
        const quests = await api.getAllQuests();
        const quest = quests.find(q => q.id === questId);
        
        if (!quest) {
            notify.error('Quête introuvable');
            return;
        }

        currentEditingQuest = quest;
        
        document.getElementById('modalTitle').textContent = 'Modifier la quête';
        document.getElementById('questTitle').value = quest.title;
        document.getElementById('questDescription').value = quest.description;
        document.getElementById('questXP').value = quest.base_xp;
        document.getElementById('questType').value = quest.type;
        
        document.getElementById('decoratorsData').value = JSON.stringify(quest.decorators);
        
        const addDecForm = document.getElementById('addDecoratorForm');
        addDecForm.classList.add('hidden');
        document.getElementById('decoratorValue').removeAttribute('required');
        
        displayDecorators(quest.decorators);
        document.getElementById('questModal').classList.add('active');
    } catch (error) {
        notify.error('Erreur lors du chargement de la quête');
        console.error(error);
    }
}

async function deleteQuest(questId, title) {
    console.log('deleteQuest called with:', questId, title);
    
    if (!confirm(`Voulez-vous vraiment supprimer la quête "${title}" ?`)) {
        console.log('Deletion cancelled by user');
        return;
    }

    try {
        console.log('Calling API to delete quest', questId);
        await api.deleteQuest(questId);
        console.log('Quest deleted successfully');
        notify.success('Quête supprimée');
        await loadAdminQuests();
        await loadAdminStats();
    } catch (error) {
        console.error('Error deleting quest:', error);
        notify.error('Erreur lors de la suppression');
    }
}

function displayDecorators(decorators) {
    const container = document.getElementById('decoratorsList');
    
    if (decorators.length === 0) {
        container.innerHTML = '<p style="color:#999;">Aucun décorateur configuré</p>';
        return;
    }

    container.innerHTML = decorators.map((dec, index) => {
        let label = '';
        if (dec.type === 'level_req') label = `Niveau ${dec.value} requis`;
        else if (dec.type === 'npc_req') label = `PNJ requis: ${dec.value}`;
        else if (dec.type === 'money_reward') label = `+${dec.value} pièces`;
        // MODIFIÉ : Ajout de l'emoji si c'est un objet
        else if (dec.type === 'item_reward') {
            const emoji = PREDEFINED_ITEMS[dec.value] || '🎁';
            label = `Objet: ${emoji} ${dec.value}`;
        }
        
        return `
            <div class="decorator-item">
                <div class="decorator-info">
                    <div class="decorator-type">${dec.type === 'level_req' || dec.type === 'npc_req' ? 'Condition' : 'Récompense'}</div>
                    <div class="decorator-value">${label}</div>
                </div>
                <button class="btn-icon" onclick="removeDecorator(${index})" title="Supprimer">🗑️</button>
            </div>
        `;
    }).join('');
}

function removeDecorator(index) {
    const decoratorsInput = document.getElementById('decoratorsData');
    const decorators = decoratorsInput.value ? JSON.parse(decoratorsInput.value) : [];
    decorators.splice(index, 1);
    decoratorsInput.value = JSON.stringify(decorators);
    displayDecorators(decorators);
}

function showAddDecoratorForm() {
    const addDecForm = document.getElementById('addDecoratorForm');
    addDecForm.classList.remove('hidden');
    
    document.getElementById('decoratorValue').setAttribute('required', 'required');
    
    updateDecoratorValueField();
}

// 🔥 FONCTION MODIFIÉE : Gère le switch Input <-> Select
function updateDecoratorValueField() {
    const type = document.getElementById('decoratorType').value;
    const oldElement = document.getElementById('decoratorValue');
    const parent = oldElement.parentElement;
    const label = parent.querySelector('label');
    
    // On garde les classes CSS pour ne pas casser le style
    const cssClass = oldElement.className || 'form-input'; // Si pas de classe, fallback

    let newElement;

    if (type === 'item_reward') {
        // Cas Objet : On veut un SELECT
        if (oldElement.tagName === 'SELECT') return; // Déjà un select, on ne fait rien

        newElement = document.createElement('select');
        newElement.id = 'decoratorValue';
        newElement.className = cssClass; // Garde le style
        newElement.required = true;

        // Option par défaut
        const defaultOpt = document.createElement('option');
        defaultOpt.value = "";
        defaultOpt.textContent = "-- Choisir un objet --";
        newElement.appendChild(defaultOpt);

        // Ajouter nos 5 objets
        for (const [name, emoji] of Object.entries(PREDEFINED_ITEMS)) {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = `${emoji} ${name}`;
            newElement.appendChild(opt);
        }

        label.textContent = "Objet à donner";

    } else {
        // Cas Normal : On veut un INPUT
        // Si c'était déjà un input, on le garde mais on change juste le type
        if (oldElement.tagName === 'INPUT') {
            newElement = oldElement; // On garde le même élément
        } else {
            // C'était un select, on recrée un input
            newElement = document.createElement('input');
            newElement.id = 'decoratorValue';
            newElement.className = cssClass;
            newElement.required = true;
        }

        // Configuration du type d'input
        if (type === 'npc_req') {
            newElement.type = 'text';
            newElement.placeholder = 'Nom du PNJ (ex: Ancien du village)';
            label.textContent = 'Nom du PNJ';
        } else if (type === 'level_req' || type === 'money_reward') {
            newElement.type = 'number';
            newElement.placeholder = 'Entrez un nombre';
            label.textContent = 'Valeur';
        }
    }

    // Remplacement dans le DOM si nécessaire
    if (oldElement !== newElement) {
        oldElement.replaceWith(newElement);
    }
}

function addDecorator() {
    const type = document.getElementById('decoratorType').value;
    const valueInput = document.getElementById('decoratorValue');
    const value = valueInput.value;

    if (!value) {
        notify.warning('Veuillez remplir la valeur');
        return;
    }

    const decoratorsInput = document.getElementById('decoratorsData');
    let decorators = [];
    
    try {
        decorators = decoratorsInput.value ? JSON.parse(decoratorsInput.value) : [];
    } catch (e) {
        console.error('Invalid decorators JSON, resetting:', e);
        decorators = [];
    }
    
    let parsedValue = value;
    
    // Conversion en nombre si nécessaire
    if (type === 'level_req' || type === 'money_reward') {
        parsedValue = parseInt(value);
        if (isNaN(parsedValue)) {
            notify.error('La valeur doit être un nombre');
            return;
        }
    }

    decorators.push({ type, value: parsedValue });
    decoratorsInput.value = JSON.stringify(decorators);
    
    displayDecorators(decorators);
    
    document.getElementById('addDecoratorForm').classList.add('hidden');
    document.getElementById('decoratorValue').removeAttribute('required');
    valueInput.value = '';
}

async function saveQuest(event) {
    event.preventDefault();

    const title = document.getElementById('questTitle').value;
    const description = document.getElementById('questDescription').value;
    const base_xp = parseInt(document.getElementById('questXP').value);
    const type = document.getElementById('questType').value;
    const decoratorsInput = document.getElementById('decoratorsData');
    const decorators = decoratorsInput.value ? JSON.parse(decoratorsInput.value) : [];

    const questData = {
        title,
        description,
        base_xp,
        type,
        decorators
    };

    console.log('Sending quest data:', questData);

    try {
        if (currentEditingQuest) {
            await api.updateQuest(currentEditingQuest.id, questData);
            notify.success('Quête modifiée avec succès');
        } else {
            await api.createQuest(questData);
            notify.success('Quête créée avec succès');
        }

        closeModal();
        await loadAdminQuests();
        await loadAdminStats();
    } catch (error) {
        notify.error('Erreur lors de la sauvegarde');
        console.error(error);
    }
}

function closeModal() {
    document.getElementById('questModal').classList.remove('active');
    
    const addDecForm = document.getElementById('addDecoratorForm');
    addDecForm.classList.add('hidden');
    document.getElementById('decoratorValue').removeAttribute('required');
    document.getElementById('decoratorValue').value = '';
}

async function fixIds() {
    if (!confirm('Voulez-vous réattribuer des IDs séquentiels à toutes les quêtes ?')) {
        return;
    }

    try {
        const result = await api.fixQuestIds();
        notify.success(result.message);
        await loadAdminQuests();
        await loadAdminStats();
    } catch (error) {
        notify.error('Erreur lors de la réparation des IDs');
        console.error(error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Admin.js loaded!'); // ✅ Test de chargement
    
    if (!auth.requireAdmin()) return;

    await loadAdminQuests();
    await loadAdminStats();

    // Event listeners
    document.getElementById('createQuestBtn').addEventListener('click', showCreateQuestModal);
    document.getElementById('questForm').addEventListener('submit', saveQuest);
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    document.getElementById('addDecoratorBtn').addEventListener('click', showAddDecoratorForm);
    document.getElementById('saveDecoratorBtn').addEventListener('click', addDecorator);
    document.getElementById('cancelDecoratorBtn').addEventListener('click', () => {
        document.getElementById('addDecoratorForm').classList.add('hidden');
        document.getElementById('decoratorValue').removeAttribute('required');
        document.getElementById('decoratorValue').value = '';
    });
    document.getElementById('fixIdsBtn').addEventListener('click', fixIds);

    // Close modal on outside click
    document.getElementById('questModal').addEventListener('click', (e) => {
        if (e.target.id === 'questModal') closeModal();
    });

    document.getElementById('decoratorType').addEventListener('change', updateDecoratorValueField);
    
    console.log('Admin.js initialized!'); // ✅ Test d'initialisation
});