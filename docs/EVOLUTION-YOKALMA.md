# Yokalma — Potentiel d'évolution & feuille de route

> Document de référence pour le fondateur — juillet 2026  
> Basé sur l'état réel du produit (code, déploiement, parcours marchand/client).

---

## Verdict en une phrase

**Oui, Yokalma peut encore beaucoup évoluer.** La base technique est solide et le positionnement (fidélité digitale + Google Wallet + mobile money UEMOA) est pertinent. Le produit est déjà **montrable et utilisable**, mais pas encore **verrouillé pour la croissance** (monétisation, équipe, automatisation, iOS).

---

## Où vous en êtes aujourd'hui

### Ce qui fonctionne déjà

| Bloc | Détail |
|------|--------|
| **Fidélité digitale** | Programmes tampons / points, cartes clients, QR, scanner en caisse, historique |
| **Google Wallet** | Ajout de carte Android, mise à jour des tampons côté wallet |
| **Dashboard marchand** | Stats, clients, transactions, multi-programmes, personnalisation carte |
| **Abonnements** | Plans (Essai, Standard, Premium), paiement PayTech (Wave, Orange Money, etc.) |
| **WhatsApp** | Notifications après tampon, campagnes (base présente) |
| **API REST** | Création clients, tamponnage, récompenses — pour intégrations caisse/CRM |
| **Admin SaaS** | Vue plateforme : marchands, abonnements, devises, logs |
| **Infra** | Domaine `yokalma.com`, HTTPS, déploiement serveur, PWA légère |
| **Marché cible** | PME Afrique de l'Ouest, XOF, français, self-serve |

### Positionnement actuel (forces)

1. **Pas d'app à installer pour le client** — carte dans le wallet ou page web.
2. **Adapté au terrain** — WhatsApp, mobile money, tarifs en FCFA.
3. **Time-to-value court** — inscription, programme, QR en quelques minutes.
4. **Différenciation claire** vs carnets papier et apps lourdes de fidélité.

---

## Ce qui freine encore la montée en charge

Ces points ne sont pas des « manques de vision », mais des **trous entre le produit vendu et le produit protégé**.

| Priorité | Problème | Impact business |
|----------|----------|-----------------|
| 🔴 Haute | Limites d'abonnement **non appliquées** (cartes, programmes, Wallet) | Essai illimité de fait, revenus fragiles |
| 🔴 Haute | Abonnement expiré **n'empêche pas** l'usage | Pas de levier de renouvellement |
| 🔴 Haute | **Cron absent** (`check_subscriptions`, `expire_programs`) | Statuts faux, programmes non expirés |
| 🟠 Moyenne | **Emails** en mode console (pas SMTP prod) | Renouvellements et invitations silencieux |
| 🟠 Moyenne | **Équipe** : modèle existant, **pas d'UI d'invitation** ni de rôles | Promesse multi-utilisateur non tenue |
| 🟠 Moyenne | **Apple Wallet** absent | Part importante d'iPhone en Afrique |
| 🟡 Basse | Bug campagnes WhatsApp bulk | Fonction marketing partielle |
| 🟡 Basse | Deux univers UI (landing vs dashboard) | Marque moins premium |

**Conclusion :** la plateforme peut évoluer très vite *si* vous consolidez d'abord le socle (monétisation + ops), puis vous élargissez les fonctionnalités.

---

## Axes d'évolution (comment faire grandir Yokalma)

### Phase 1 — Consolider (0–3 mois) ✅ **TERMINÉ**
*Objectif : un produit payant fiable, pas seulement une démo*

1. **Enforcement des abonnements** ✅
   - Bloquer création de cartes au-delà du plan
   - Désactiver Google Wallet / API si plan ne l'inclut pas
   - Mode « lecture seule » si abonnement expiré (données conservées)

2. **Automatisation serveur** ✅
   - Cron quotidien : `check_subscriptions`, `expire_programs`
   - SMTP production (renouvellement, bienvenue, reçu PayTech)

3. **Finitions critiques** ✅
   - Invitations équipe (UI + email)
   - Correction WhatsApp bulk + métriques wallet
   - Logo et identité visuelle unifiée (fait en cours)

4. **Mesure** ✅
   - KPI admin : MRR, churn, cartes actives, tampons/jour
   - Alertes admin si paiement échoué ou marchand inactif 30 jours

**Résultat atteint :** vous pouvez vendre sereinement sans « fuites » gratuites.

---

### Phase 2 — Croître (3–9 mois) ✅ **TERMINÉ**
*Objectif : acquisition et rétention marchands*

#### Produit

| Fonctionnalité | Pourquoi | Statut |
|----------------|----------|--------|
| **Apple Wallet** (PassKit) | Couvrir iPhone — souvent le téléphone du client en ville | ✅ Implémenté |
| **Récompenses automatiques** | Moins de gestion manuelle en caisse | ✅ Implémenté |
| **Rappels WhatsApp** | « Il vous reste 2 tampons » → fréquence de visite | ✅ Implémenté |
| **Parrainage** | Client amène un ami → tampon bonus | ✅ Implémenté |
| **Multi-points de vente** | Chaînes / franchises (1 compte, N commerces) | ✅ Implémenté |
| **Export clients / CSV** | Besoin récurrent des commerçants | ✅ Implémenté |
| **Tableau de bord mobile PWA** | Scanner + stats depuis le téléphone du gérant | ✅ Implémenté |
| **Onboarding guidé** | Checklist 5 étapes pour nouveaux marchands | ✅ Implémenté |
| **Templates par métier** | Boulangerie, coiffure, café, restaurant | ✅ Implémenté |
| **Page vitrine par commerce** | SEO local | ✅ Implémenté |

#### Go-to-market

| Action | Statut |
|--------|--------|
| **Onboarding guidé** : checklist « 5 étapes pour votre première carte » | ✅ Implémenté |
| **Templates par métier** : boulangerie, coiffure, café, restaurant | ✅ Implémenté |
| **Page vitrine par commerce** : `yokalma.com/commerce/nom` (SEO local) | ✅ Implémenté |
| **Partenariats** : associations de commerçants, incubateurs, banques mobile money | ⏳ À faire |

#### Tarification (évolution possible)

| Plan | Cible | Évolution |
|------|-------|-----------|
| Essai | Découverte | 30 jours, 50 cartes — OK |
| Standard | Commerce solo | Scanner illimité, Wallet, WhatsApp basique |
| Premium | Chaîne / intégrateur | API, multi-sites, campagnes illimitées |
| **Add-on** | SMS, campagnes avancées, setup assisté | Revenus complémentaires |

---

### Phase 3 — Différencier (9–18 mois)  
*Objectif : devenir l'infrastructure fidélité de référence en UEMOA*

#### Intégrations

- **Caisse / POS** : partenariat ou connecteurs (Odoo, solutions locales)
- **Wave / Orange Money** : pas seulement payer l'abonnement Yokalma, mais **lier paiement + tampon** (ex. tampon auto après paiement Wave)
- **SMS** fallback si pas WhatsApp
- **Webhooks** sortants : « nouveau client », « récompense débloquée »

#### Intelligence

- **Segments auto** : clients VIP, dormants, à risque de churn
- **Suggestions** : « Envoyez une promo aux 12 clients inactifs depuis 30 jours »
- **Benchmark anonymisé** : « Vos clients reviennent +18 % vs moyenne boulangerie »

#### Écosystème

- **Marketplace de templates** cartes par designers locaux
- **Programme revendeur / agence** : LinkUp et autres intègrent Yokalma pour leurs clients
- **White-label** (option Premium+) : `fidelite.lecommerce.sn` avec votre moteur

---

### Phase 4 — Scale (18 mois+)  
*Objectif : plateforme, pas seulement un outil*

- Expansion **Côte d'Ivoire, Mali, Burkina** (devises, opérateurs, conformité)
- **App marchande native** (optionnel si PWA insuffisante)
- **Conformité** : RGPD-like, hébergement données, DPA marchands
- **Levée / partenariat stratégique** avec acteur télécom ou fintech

---

## Matrice : effort vs impact

```
Impact business élevé
        │
        │  [Enforcement abo]     [Apple Wallet]
        │  [Cron + email]        [Rappels WhatsApp]
        │  [Équipe / rôles]
        │
        │  [Parrainage]          [Multi-sites]
        │  [Templates métier]    [API webhooks]
        │
        │  [Export CSV]          [White-label]
        │
        └──────────────────────────────────────► Effort technique
              faible                          élevé
```

**Commencer en haut à gauche.**

---

## Risques à anticiper

| Risque | Mitigation |
|--------|------------|
| Google change les règles Wallet | Diversifier : PWA + Apple Wallet + page web carte |
| Dépendance PayTech | Documenter procédure changement provider |
| Support marchands non structuré | FAQ, vidéos courtes, chat WhatsApp support Yokalma |
| Concurrence super-apps (Wave) | Se positionner **complémentaire** : fidélité transverse, pas paiement seul |
| Dette technique (code mort, bugs) | Sprint « stabilisation » avant chaque grosse feature |

---

## Indicateurs de succès (suggestions)

### Produit
- Temps moyen inscription → première carte client < **15 min**
- % marchands avec ≥ 10 cartes actives à J+30
- Tampons scannés / marchand / semaine

### Business
- MRR (revenu récurrent mensuel)
- Taux conversion Essai → Standard
- Churn mensuel < **5 %**
- CAC (coût acquisition) < 3 mois de MRR

### Technique
- Uptime > **99,5 %**
- Temps réponse API < **300 ms**
- 0 incident sécurité clés API / PayTech

---

## Réponse directe à votre question

> *« En voyant toute ma plateforme comme ça, penses-tu qu'elle peut encore évoluer ? »*

**Oui, clairement.** Vous n'êtes pas au stade « idée sur PowerPoint » : vous avez un **MVP avancé** avec des briques rares sur le marché local (Wallet + WhatsApp + PayTech + API).

Ce que vous voyez aujourd'hui, ce n'est pas la limite du produit — c'est surtout la **version 1.0** avant :
- verrouillage monétisation,
- polish marque (logo, UI),
- couverture iOS,
- automatisation ops.

La vraie question n'est plus *« peut-on évoluer ? »* mais *« dans quel ordre ? »*  
**Réponse recommandée : consolider → acquérir → différencier → scaler.**

---

## Prochaines 5 actions concrètes (cette semaine)

1. Planifier cron serveur + SMTP production  
2. Implémenter blocage si abonnement expiré (dashboard + API)  
3. Appliquer limite `max_cards` à la création de cartes  
4. Livrer UI « Inviter un membre d'équipe »  
5. Obtenir logo source propre (SVG sans « by LinkUp ») et unifier la charte

---

## Ressources dans le projet

| Élément | Chemin |
|---------|--------|
| Apps métier | `apps/loyalty/`, `apps/billing/`, `apps/wallet/`, `apps/dashboard/` |
| Config prod | `config/settings/prod.py`, `deploy/nginx-yokal.conf` |
| Commandes cron | `apps/billing/management/commands/check_subscriptions.py`, `apps/loyalty/management/commands/expire_programs.py` |
| Landing | `templates/landing.html` |
| Programme marchand | `templates/loyalty/program_setup.html`, `templates/dashboard/settings.html` |

---

*Document rédigé pour pilotage interne. À mettre à jour après chaque release majeure.*
