# Mumble Link Core
*Ce programme permet la création de serveurs mumbles, l'enregistrement et la gestion de ces membres. Il a pour objectif d'être utilisé en plus des mods utilisant la fonctionnalité Link de Mumble notamment le mod [MumbleLink](https://legacy.curseforge.com/minecraft/mc-mods/mumblelink) pour Minecraft de [snipingcoward](https://legacy.curseforge.com/members/snipingcoward).*
## Support
En cas de soucis lors de l'installation ou de l'utilisation, vous pouvez m'envoyer un message sur [Discord](https://discord.ezalys.fr), j'essaierai de vous aider dans la mesure du possible !
## Installation
Vous aurez besoin d'un serveur Linux ([Debian](https://www.debian.org) recommandé), ainsi que Python 3.9 de préférence.

1. Installez Python 3.9:
		Suivez le tutoriel de Linuxize [disponible ici](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/).
2. Installez Git:
		Avec la commande: `sudo apt-get install git`
		
3. Clonez le programme:
		Avec la commande: `git clone https://github.com/EliottBovel/MumbleLinkCore.git`
		
4. Rentrez dans le dossier, puis installez les dépendance grâce à PIP:
		Avec la commande: `pip install requirements.txt` 
		
5. Installez le serveur Murmur sur le même serveur:
		Pour cela, vous avez deux solutions:
		- [RECOMMANDÉ] Utiliser le build disponible dans l'archive [murmur-static_x86-1.3.4.tar.bz2](https://github.com/EliottBovel/MumbleLinkCore/blob/master/murmur-static_x86-1.3.4.tar.bz2 "murmur-static_x86-1.3.4.tar.bz2") que vous avez télécharger avec le programme.
			Dans ce cas, il faudra extraire l'archive puis executer la commande `chmod +x murmur.x86` pour pouvoir lancer le serveur Murmur.
		- Installer une version différente via une autre source. (Pas très difficile, je vous laisse chercher sur Google.)

6. Configurez le serveur Murmur:
	Editez le fichier murmur.ini avec la commande `nano murmur.ini` (ou un autre outils).
	Voici les changements à faire:
	- Décommenter la ligne `ice="tcp -h 127.0.0.1 -p 6502"` en enlevant le ; (Changez le port si vous voulez)
	- Commenter la ligne `icesecretwrite=` en ajoutant un ; au début de la ligne.
	- Décommenter et changer la ligne `;autobanAttempts=10` en `autobanAttempts=0`
	- Si vous avez un autre serveur Murmur (Mumble) sur la même machine ou que vous voulez changer le port de base des mumbles, c'est aussi dans ce fichier. (Pour chaque mumble, le port est incrémenter de 1)

7. Configurez le programme:
		Editez le fichier config.ini à la racine du programme avec la commande `nano config.ini` en modifiant selon votre cas:

		- [MURMUR] ice_file: Emplacement vers le fichier ICE (laisser d'origine sauf si vous savez ce que vous faites)
		- [MURMUR] ip: Adresse IP vers le serveur Murmur (laisser d'origine sauf si vous avez installer le serveur Murmur sur un autre serveur)
		- [MURMUR] port: Port vers le serveur Murmur (A changer si vous l'avez fait plus haut.)
		- [MUMBLE] default_name: Nom du canal Root si le client n'en précise aucun à la requête de création.
		- /!\ [MUMBLE] superuser_password: Mot de passe du compte SuperUser (administrateur).
		- /!\ [MUMBLE] server_password: Mot de passe pour se connecter sans être enregistré.
		- /!\ [MUMBLE] public_ip: IP à laquelle les joueurs devront se connecter (c'est ici que vous mettez soit l'ip public de votre machine soit votre nom de domaine qui redirige vers celle-ci)
		- [MUMBLE] first_port: Port du premier mumble créé (incrémenté de 1 par mumble)
		- [SOCKET] ip: IP à laquelle le socket écoute. (laisser d'origine sauf si vous savez ce que vous faites)
		- [SOCKET] port: Port auquel le socket écoute. (changez le aussi dans votre client si vous le changez la)
		- [WEB] ip: IP à laquelle le seveur web écoute. (laisser d'origine sauf si vous savez ce que vous faites)
		- [WEB] port: Port auquel le serveur web écoute.
		- /!\ [AUTH] api-key: Clef d'api à utiliser pour communiquer avec le programme via le socket.
		- [LOG] A changer en false (non) ou en true (oui) si vous activer ou désactiver certaines logs.

Les lignes commencant par /!\ sont les plus importants à vérifier.
En cas de mises à jours, vérifiez que toutes les valeurs sont bien présentes et correctement renseignés.

N'oubliez par d'ouvrir les ports du socket et du web !

8. Lancer le serveur Murmur PUIS le programme.
		Vous pouvez utiliser le programme [screen](https://wiki.debian.org/fr/Screen) pour les laisser actifs ou tout autre moyen.
		Si vous avez utilisez l'archive pour le serveur Murmur, lancer le serveur avec la commande: `./murmur.x86`
		Pour lancer le programme, utilisez la commande: `python3.9 main.py`

## Modifier les pages Webs.
Il y a deux pages html, une pour se connecter ([web/index.html](https://github.com/EliottBovel/MumbleLinkCore/blob/master/web/index.html)) et une en cas d'erreur ([web/error.html](https://github.com/EliottBovel/MumbleLinkCore/blob/master/web/error.html)).
Vous pouvez les modifier à votre guise en gardant le nom de l'auteur du programme et un lien vers ce [repo](https://discord.ezalys.fr/) ou vers mon [Discord](https://github.com/EliottBovel/MumbleLinkCore). 
Je ne demande aucun crédit en jeux ou sur mumble, seulement sur les pages webs. 
Merci de respecter ma seule demande en échange d'heures de travails offertes.

Voici les différentes variables que vous pouvez placer:

 - {ip} : IP du Mumble (la public_ip dans le config.ini);
 - {port} : Port du Mumble;
 - {username}: Nom d'utilisateur du joueur;
 - {password}: Mot de passe du joueur;
 - {link}: Lien complet pour se connecter au Mumble.

## Client Socket prêt à l'emploi 

Voici la liste des clients que vous pouvez utiliser gratuitement:

- Plugin Minecraft Spigot 1.8.9 (par [EliottBvl](https://github.com/EliottBovel)): [Lien GitHub](https://github.com/EliottBovel/MumbleLinkClient/tree/master)

Si vous en développez d'autres, n'hésitez pas à me le dire, je les ajouterais !

## Comment faire un Client Socket
*En cours de rédaction. 
En attendant, les plus impatients peuvent analyser le programme (et le fichier [socketManager.py](https://github.com/EliottBovel/MumbleLinkCore/blob/master/socketManager.py))*

## Liste des Serveurs Minecraft (ou Discord) utilisant le programme:

 - [Ezalys](http://discord.ezalys.fr) : UHC Minecraft

N'hésitez pas à me contacter sur Discord pour ajouter votre serveur ici ! Discord: EliottBvl

## TODO 
*En cours de rédaction.*

## Modification du Programme
Chacun est libre de modifier le programme à sa guise, en respectant  mon souhait de rester créditer sur les pages Webs (ou autre moyen affichant les informations de connection).

Je n'apporterai pas de support aux programmes différents de celui sur ce git.
Si vous voulez participer à l'amélioration du programme, n'hésitez pas à proposer vos changements sur GitHub !

Merci à vous et profitez bien de ce programme !

    

