// Admin Dashboard Logic

let currentEditingQuest = null;

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

    tbody.innerHTML = quests.map(quest => `
        <tr>
            <td>${quest.id}</td>
            <td><strong>${quest.title}</strong></td>
            <td>${quest.type}</td>
            <td>${quest.base_xp}</td>
            <td>${quest.decorators.length}</td>
            <td>
                <button class="btn btn-primary" onclick="editQuest(${quest.id})" style="margin-right: 0.5rem; padding: 0.5rem 1rem;">
                    ✏️ Modifier
                </button>
                <button class="btn btn-danger" onclick="deleteQuest(${quest.id}, '${quest.title}')" style="padding: 0.5rem 1rem;">
                    🗑️ Supprimer
                </button>
            </td>
        </tr>
    `).join('');
}

async function loadAdminStats() {
    try {
        const stats = await api.getAdminStats();
        document.getElementById('totalUsers').textContent = stats.total_users;
        document.getElementById('totalQuests').textContent = stats.total_quests;
    } catch (error) {
        console.error('Erreur stats:', error);
    }
}

function showCreateQuestModal() {
    document.getElementById('modalTitle').textContent = 'Créer une nouvelle quête';
    document.getElementById('questForm').reset();
    document.getElementById('decoratorsList').innerHTML = '<p style="color:#999;">Aucun décorateur configuré</p>';
    document.getElementById('decoratorsData').value = '[]';
    
    // ✅ CORRECTION : Cacher le formulaire et retirer required
    const addDecForm = document.getElementById('addDecoratorForm');
    addDecForm.classList.add('hidden');
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
        
        // ✅ CORRECTION : Cacher le formulaire et retirer required
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
    if (!confirm(`Voulez-vous vraiment supprimer la quête "${title}" ?`)) {
        return;
    }

    try {
        await api.deleteQuest(questId);
        notify.success('Quête supprimée');
        await loadAdminQuests();
    } catch (error) {
        notify.error('Erreur lors de la suppression');
        console.error(error);
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
        else if (dec.type === 'item_reward') label = `Objet: ${dec.value}`;
        
        return `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f8f9fa; border-radius: 4px; margin-bottom: 0.5rem;">
                <span>${label}</span>
                <button class="btn btn-danger" onclick="removeDecorator(${index})" style="padding: 0.25rem 0.75rem;">×</button>
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
    
    // ✅ CORRECTION : Ajouter required quand on affiche le formulaire
    document.getElementById('decoratorValue').setAttribute('required', 'required');
    
    updateDecoratorValueField();
}

function updateDecoratorValueField() {
    const type = document.getElementById('decoratorType').value;
    const valueContainer = document.getElementById('decoratorValue').parentElement;
    const input = document.getElementById('decoratorValue');
    
    if (type === 'npc_req') {
        input.type = 'text';
        input.placeholder = 'Nom du PNJ (ex: Ancien du village)';
        valueContainer.querySelector('label').textContent = 'Nom du PNJ';
    } else if (type === 'level_req' || type === 'money_reward') {
        input.type = 'number';
        input.placeholder = 'Entrez un nombre';
        valueContainer.querySelector('label').textContent = 'Valeur';
    } else {
        input.type = 'text';
        input.placeholder = 'Entrez le nom de l\'objet';
        valueContainer.querySelector('label').textContent = 'Nom de l\'objet';
    }
}

function addDecorator() {
    const type = document.getElementById('decoratorType').value;
    const value = document.getElementById('decoratorValue').value;

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
    
    // ✅ CORRECTION : Cacher et retirer required après ajout
    document.getElementById('addDecoratorForm').classList.add('hidden');
    document.getElementById('decoratorValue').removeAttribute('required');
    document.getElementById('decoratorValue').value = '';
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

    console.log('Sending quest data:', questData); // ✅ Debug

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
    } catch (error) {
        notify.error('Erreur lors de la sauvegarde');
        console.error(error);
    }
}

function closeModal() {
    document.getElementById('questModal').classList.remove('active');
    
    // ✅ CORRECTION : Nettoyer complètement le formulaire
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
    } catch (error) {
        notify.error('Erreur lors de la réparation des IDs');
        console.error(error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
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
        // ✅ CORRECTION : Retirer required lors de l'annulation
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
});