commande project

quest_admin.py
create	Aucun	Lance l'assistant interactif pour créer une nouvelle quête étape par étape.
list	Aucun	Affiche un tableau de toutes les quêtes enregistrées dans la base de données.
delete	QUEST_ID	Supprime définitivement la quête correspondant à l'ID donné (ex: 1).
modify	QUEST_ID	Permet de changer le titre et l'XP d'une quête existante.




quest_manager.py

status	Aucun	Affiche les stats du joueur (Niveau, XP, Argent, Inventaire, PNJ vu).
list-quests	Aucun	Affiche les quêtes disponibles pour le joueur (celles chargées depuis le JSON).
do-quest	QUEST_ID	Tente d'accomplir la quête. Échoue si les conditions (Niveau/PNJ) ne sont pas remplies.
talk-npc	Aucun	Simule le dialogue avec le PNJ (débloque les quêtes qui demandent npc_req).
cheat-level	LEVEL	Triche : Change instantanément le niveau du joueur (ex: pour tester une quête haut niveau).