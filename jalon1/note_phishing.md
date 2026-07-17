# Note de synthèse — Le phishing et les URLs malveillantes

*Stage PFA été 2026 — Jalon 1 · Système de détection et d'alerte précoce des cybermenaces ciblant les PME*

## 1. Qu'est-ce que le phishing ?

Le phishing (ou « hameçonnage » en français) est une technique d'attaque dans laquelle un cybercriminel se fait passer pour un organisme de confiance — une banque, un fournisseur, un service public, ou même un collègue — afin de pousser la victime à faire quelque chose qui va contre son intérêt : donner son mot de passe, communiquer ses coordonnées bancaires, ouvrir une pièce jointe piégée ou cliquer sur un lien malveillant.

Le nom vient de l'anglais *fishing* (pêche) : l'attaquant « lance un appât » (un e-mail ou un SMS crédible) et attend qu'une victime « morde à l'hameçon ». L'attaque ne vise pas une faille technique du système, mais une faiblesse humaine : la confiance, l'urgence, la peur ou la simple inattention.

Un e-mail de phishing typique ressemble à ceci :

> « Votre compte sera suspendu dans 24 heures. Cliquez ici pour confirmer vos informations : http://banque-securite-verification.xyz/login »

Le lien mène vers une **fausse page** qui imite le site légitime. Si la victime y saisit ses identifiants, l'attaquant les récupère directement.

## 2. Qu'est-ce qu'une URL malveillante ?

Une URL (adresse web) malveillante est un lien qui conduit vers un contenu dangereux. On en distingue principalement deux familles :

- **URL de phishing** : elle mène vers une fausse page de connexion qui imite un site légitime pour voler des identifiants ou des données bancaires.
- **URL de distribution de malware** : elle sert à télécharger un logiciel malveillant (virus, ransomware, cheval de Troie) sur la machine de la victime, parfois sans qu'elle s'en rende compte.

Quelques signes qui doivent alerter :

- Un **nom de domaine qui imite** un site connu avec une petite variation : `paypa1.com` au lieu de `paypal.com`, `micros0ft-support.net`, etc.
- Une **adresse IP brute** à la place d'un nom de domaine : `http://42.231.90.113:57377/bin.sh`.
- Des **sous-domaines trompeurs** : dans `banque.fr.verification-compte.xyz`, le vrai domaine est `verification-compte.xyz`, pas `banque.fr`.
- L'**absence de HTTPS**, des caractères inhabituels, des URLs très longues ou raccourcies (bit.ly, etc.) qui masquent la vraie destination.

Ces caractéristiques observables sont importantes pour la suite du projet : au Jalon 2, ce sont exactement ce genre d'indices (longueur de l'URL, présence d'une IP, nombre de sous-domaines...) qui serviront de **variables d'entrée à un modèle de Machine Learning** pour classer automatiquement une URL comme légitime ou suspecte.

## 3. Pourquoi les PME sont-elles des cibles privilégiées ?

- Elles n'ont généralement **pas d'équipe de cybersécurité dédiée** ni d'outils de détection avancés.
- Leurs employés sont **moins formés** à reconnaître les tentatives de phishing.
- Elles détiennent pourtant des **données de valeur** (comptes bancaires, données clients, accès à de plus grandes entreprises dont elles sont fournisseurs).
- Une attaque réussie (ex. ransomware entré par un e-mail de phishing) peut leur être fatale, car elles ont peu de capacité de récupération.

C'est tout l'intérêt de ce projet : offrir aux PME un outil **simple et peu coûteux** qui les prévient rapidement des menaces émergentes.

## 4. La Threat Intelligence : savoir avant d'être attaqué

La *Threat Intelligence* (renseignement sur les menaces) consiste à collecter et partager des informations sur les menaces connues : URLs malveillantes, adresses IP d'attaquants, fichiers infectés... Des plateformes communautaires publient gratuitement ces listes, alimentées par des chercheurs en sécurité du monde entier :

- **PhishTank** (https://phishtank.org) — base communautaire d'URLs de phishing vérifiées par des volontaires. Le flux CSV des URLs de phishing en ligne est **gratuit et sans clé d'API**, c'est la source retenue pour ce jalon car elle correspond exactement à la menace étudiée. Chaque entrée indique aussi la marque imitée (`target`), ce qui aide à comprendre qui les attaquants ciblent.
- **URLhaus** (https://urlhaus.abuse.ch) — projet d'abuse.ch qui recense les URLs distribuant des malwares (autre famille d'URLs malveillantes, utile comme extension future).

## 5. Ce que fait le script de ce jalon

Le script `telecharger_urls.py` réalise la première brique du prototype :

1. Il **télécharge** le flux CSV des URLs de phishing vérifiées et en ligne depuis PhishTank (bibliothèque `requests`).
2. Il **charge** les données dans un tableau `pandas`.
3. Il **affiche un résumé** : nombre d'URLs, marques les plus imitées, dernières URLs signalées.
4. Il **sauvegarde** les données dans un fichier CSV horodaté dans le dossier `data/`, qui servira de matière première aux jalons suivants.

**Exécution :** `python telecharger_urls.py` (nécessite `pandas` et `requests`).

---
*Rédigé dans le cadre du Jalon 1 (15–31 juillet 2026). Encadrant principal : Pr. Youssef Bentaleb — Co-encadrante ML : Pr. Mehdia Ajana.*
