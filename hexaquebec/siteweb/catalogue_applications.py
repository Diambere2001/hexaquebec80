# siteweb/catalogue_applications.py

"""
Catalogue complet des solutions numériques proposées par HexaQuébec.

Ce fichier contient :
- toutes les catégories d’applications ;
- les trois niveaux de qualité ;
- les prix indicatifs ;
- les délais estimés ;
- les fonctionnalités incluses.

Utilisation dans views.py :

    from .catalogue_applications import (
        CATALOGUE_APPLICATIONS,
        obtenir_offre_complete,
    )
"""


CATALOGUE_APPLICATIONS = {

    # ============================================================
    # 1. RESTAURANT
    # ============================================================

    "restaurant": {
        "nom": "Restaurant et commande",
        "nom_court": "Restaurant",
        "icone": "fa-utensils",
        "couleur": "#ff7a59",

        "description": (
            "Présentez votre menu, recevez des commandes et gérez "
            "les activités de votre restaurant depuis une seule solution."
        ),

        "public": (
            "Restaurants, cafés, pâtisseries, fast-foods "
            "et services traiteur"
        ),

        "prix_depart": 5000,

        "forfaits": {

            "essentiel": {
                "nom": "Essentiel",
                "prix": 5000,
                "devise": "CAD",
                "delai": "3 à 5 semaines",
                "badge": "Pour commencer",
                "recommande": False,

                "fonctionnalites": [
                    "Site responsive pour ordinateur, tablette et mobile",
                    "Présentation du restaurant",
                    "Présentation de l’équipe",
                    "Menu avec catégories",
                    "Photos des plats",
                    "Descriptions et prix des plats",
                    "Commande simple par formulaire",
                    "Commande par WhatsApp",
                    "Horaires d’ouverture",
                    "Coordonnées du restaurant",
                    "Carte et localisation",
                    "Administration du menu",
                    "Formulaire de contact",
                    "Référencement SEO de base",
                ],
            },

            "professionnel": {
                "nom": "Professionnel",
                "prix": 9000,
                "devise": "CAD",
                "delai": "5 à 8 semaines",
                "badge": "Le plus choisi",
                "recommande": True,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Essentiel",
                    "Commande complète en ligne",
                    "Panier de commande",
                    "Paiement sécurisé en ligne",
                    "Livraison à domicile",
                    "Ramassage sur place",
                    "Comptes clients",
                    "Historique des commandes",
                    "Codes promotionnels",
                    "Emails de confirmation automatiques",
                    "Gestion des zones de livraison",
                    "Gestion des frais de livraison",
                    "Tableau de bord des ventes",
                    "Gestion du statut des commandes",
                ],
            },

            "premium": {
                "nom": "Premium",
                "prix": 18000,
                "devise": "CAD",
                "delai": "8 à 12 semaines",
                "badge": "Solution complète",
                "recommande": False,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Professionnel",
                    "Application web installable PWA",
                    "Gestion de plusieurs restaurants",
                    "Gestion de plusieurs succursales",
                    "Programme de fidélité",
                    "Points et récompenses clients",
                    "Notifications avancées",
                    "Suivi du statut des commandes",
                    "Rapports financiers détaillés",
                    "Statistiques des produits les plus vendus",
                    "Version multilingue",
                    "Intégrations personnalisées",
                    "Gestion avancée des employés",
                ],
            },
        },
    },

    # ============================================================
    # 2. E-COMMERCE
    # ============================================================

    "ecommerce": {
        "nom": "Boutique e-commerce",
        "nom_court": "E-commerce",
        "icone": "fa-cart-shopping",
        "couleur": "#3478f6",

        "description": (
            "Vendez vos produits en ligne avec un catalogue professionnel, "
            "un panier, des paiements et une gestion complète des commandes."
        ),

        "public": (
            "Boutiques, marques, créateurs, commerçants "
            "et commerces de détail"
        ),

        "prix_depart": 4000,

        "forfaits": {

            "essentiel": {
                "nom": "Essentiel",
                "prix": 4000,
                "devise": "CAD",
                "delai": "4 à 6 semaines",
                "badge": "Petite boutique",
                "recommande": False,

                "fonctionnalites": [
                    "Boutique responsive",
                    "Page d’accueil professionnelle",
                    "Catalogue de produits",
                    "Catégories de produits",
                    "Fiches produits",
                    "Photos des produits",
                    "Description et prix",
                    "Gestion du stock simple",
                    "Panier d’achat",
                    "Paiement sécurisé en ligne",
                    "Gestion des commandes",
                    "Emails de confirmation",
                    "Tableau de bord administrateur",
                    "Formulaire de contact",
                ],
            },

            "professionnel": {
                "nom": "Professionnel",
                "prix": 6000,
                "devise": "CAD",
                "delai": "6 à 9 semaines",
                "badge": "Le plus choisi",
                "recommande": True,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Essentiel",
                    "Comptes clients",
                    "Connexion et inscription",
                    "Historique des commandes",
                    "Liste des produits favoris",
                    "Promotions et coupons",
                    "Gestion avancée du stock",
                    "Variantes de produits",
                    "Tailles, couleurs et modèles",
                    "Factures PDF automatiques",
                    "Avis et évaluations",
                    "Suivi des livraisons",
                    "Statistiques de ventes",
                    "Produits similaires",
                    "Produits recommandés",
                ],
            },

            "premium": {
                "nom": "Premium",
                "prix": 15000,
                "devise": "CAD",
                "delai": "9 à 14 semaines",
                "badge": "Grande boutique",
                "recommande": False,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Professionnel",
                    "Application mobile ou PWA",
                    "Abonnements mensuels",
                    "Paiements récurrents",
                    "Gestion de plusieurs entrepôts",
                    "Gestion de plusieurs administrateurs",
                    "Programme de fidélité",
                    "Points et récompenses",
                    "Recommandations intelligentes",
                    "Version multilingue",
                    "Gestion multidevise",
                    "Rapports financiers avancés",
                    "Intégrations comptables",
                    "Intégrations logistiques",
                    "API personnalisée",
                ],
            },
        },
    },

    # ============================================================
    # 3. MARKETPLACE MULTIVENDEUR
    # ============================================================

    "marketplace": {
        "nom": "Marketplace multivendeur",
        "nom_court": "Marketplace",
        "icone": "fa-store",
        "couleur": "#8b5cf6",

        "description": (
            "Regroupez plusieurs vendeurs, leurs boutiques et leurs produits "
            "dans une plateforme avec commandes, commissions et tableaux de bord."
        ),

        "public": (
            "Plateformes commerciales, réseaux de vendeurs, "
            "associations et projets nationaux"
        ),

        "prix_depart": 9000,

        "forfaits": {

            "essentiel": {
                "nom": "Essentiel",
                "prix": 20000,
                "devise": "CAD",
                "delai": "8 à 12 semaines",
                "badge": "Marketplace initiale",
                "recommande": False,

                "fonctionnalites": [
                    "Inscription des vendeurs",
                    "Connexion des vendeurs",
                    "Création des boutiques",
                    "Gestion du profil vendeur",
                    "Ajout des produits",
                    "Modification des produits",
                    "Suppression des produits",
                    "Catégories de produits",
                    "Recherche et filtres",
                    "Panier client",
                    "Commandes clients",
                    "Validation des vendeurs",
                    "Administration générale",
                    "Notifications email",
                    "Gestion simple des boutiques",
                ],
            },

            "professionnel": {
                "nom": "Professionnel",
                "prix": 20000,
                "devise": "CAD",
                "delai": "12 à 18 semaines",
                "badge": "Le plus choisi",
                "recommande": True,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Essentiel",
                    "Tableau de bord vendeur",
                    "Statistiques des ventes vendeur",
                    "Commission automatique de la plateforme",
                    "Gestion des commissions",
                    "Messagerie client-vendeur",
                    "Avis et évaluations",
                    "Gestion des litiges",
                    "Rapports financiers",
                    "Gestion des paiements vendeurs",
                    "Factures PDF",
                    "Produits mis en avant",
                    "Boutiques vérifiées",
                    "Gestion avancée des commandes",
                    "Notifications automatiques",
                ],
            },

            "premium": {
                "nom": "Premium",
                "prix": 25000,
                "devise": "CAD",
                "delai": "18 à 26 semaines",
                "badge": "Grande plateforme",
                "recommande": False,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Professionnel",
                    "Application Android",
                    "Application iOS",
                    "Application web complète",
                    "Vérification d’identité des vendeurs",
                    "Documents d’identité",
                    "Portefeuille vendeur",
                    "Solde et historique financier",
                    "Livraison avancée",
                    "Suivi des livraisons",
                    "Publicités payantes",
                    "Produits sponsorisés",
                    "Boutiques sponsorisées",
                    "Version multilingue",
                    "Gestion de plusieurs pays",
                    "Gestion multidevise",
                    "Architecture évolutive",
                    "Haute capacité d’utilisateurs",
                    "Intégrations de paiements personnalisées",
                ],
            },
        },
    },

    # ============================================================
    # 4. RÉSERVATION ET RENDEZ-VOUS
    # ============================================================

    "reservation": {
        "nom": "Réservation et rendez-vous",
        "nom_court": "Réservation",
        "icone": "fa-calendar-check",
        "couleur": "#f59e0b",

        "description": (
            "Permettez à vos clients de réserver des rendez-vous, "
            "des services, des chambres ou des événements."
        ),

        "public": (
            "Salons de coiffure, cliniques, hôtels, consultants, "
            "professionnels et organisateurs d’événements"
        ),

        "prix_depart": 3000,

        "forfaits": {

            "essentiel": {
                "nom": "Essentiel",
                "prix": 3000,
                "devise": "CAD",
                "delai": "4 à 6 semaines",
                "badge": "Agenda simple",
                "recommande": False,

                "fonctionnalites": [
                    "Présentation de l’entreprise",
                    "Présentation des services",
                    "Calendrier de disponibilités",
                    "Réservation en ligne",
                    "Choix de la date",
                    "Choix de l’heure",
                    "Confirmation par email",
                    "Gestion des rendez-vous",
                    "Modification des réservations",
                    "Annulation des réservations",
                    "Espace administrateur",
                    "Site responsive",
                ],
            },

            "professionnel": {
                "nom": "Professionnel",
                "prix": 5500,
                "devise": "CAD",
                "delai": "6 à 10 semaines",
                "badge": "Le plus choisi",
                "recommande": True,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Essentiel",
                    "Paiement en ligne",
                    "Dépôt obligatoire",
                    "Gestion de plusieurs employés",
                    "Gestion de plusieurs ressources",
                    "Rappels automatiques",
                    "Emails de rappel",
                    "Comptes clients",
                    "Historique des réservations",
                    "Forfaits et promotions",
                    "Rapports d’activité",
                    "Gestion avancée des horaires",
                    "Synchronisation avec calendrier",
                    "Gestion des absences",
                ],
            },

            "premium": {
                "nom": "Premium",
                "prix": 9000,
                "devise": "CAD",
                "delai": "10 à 15 semaines",
                "badge": "Réseau complet",
                "recommande": False,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Professionnel",
                    "Gestion de plusieurs établissements",
                    "Application mobile ou PWA",
                    "Liste d’attente intelligente",
                    "Abonnements mensuels",
                    "Cartes de membre",
                    "Automatisations personnalisées",
                    "Statistiques avancées",
                    "Rapports financiers",
                    "Notifications SMS selon intégration",
                    "Intégrations externes",
                    "API personnalisée",
                    "Gestion de plusieurs administrateurs",
                ],
            },
        },
    },

    # ============================================================
    # 5. IMMOBILIER
    # ============================================================

    "immobilier": {
        "nom": "Immobilier et gestion locative",
        "nom_court": "Immobilier",
        "icone": "fa-building",
        "couleur": "#0ea5e9",

        "description": (
            "Présentez des propriétés ou gérez vos propriétaires, locataires, "
            "contrats, loyers, paiements et rapports financiers."
        ),

        "public": (
            "Agences immobilières, promoteurs, propriétaires "
            "et gestionnaires immobiliers"
        ),

        "prix_depart": 3500,

        "forfaits": {

            "essentiel": {
                "nom": "Essentiel",
                "prix": 3500,
                "devise": "CAD",
                "delai": "5 à 8 semaines",
                "badge": "Vitrine immobilière",
                "recommande": False,

                "fonctionnalites": [
                    "Présentation de l’agence",
                    "Présentation des agents",
                    "Liste des propriétés",
                    "Catégories de propriétés",
                    "Recherche et filtres",
                    "Fiches détaillées des propriétés",
                    "Galeries photos",
                    "Prix et caractéristiques",
                    "Demandes de visite",
                    "Carte et localisation",
                    "Administration des annonces",
                    "Site responsive",
                    "Formulaire de contact",
                ],
            },

            "professionnel": {
                "nom": "Professionnel",
                "prix": 6500,
                "devise": "CAD",
                "delai": "8 à 13 semaines",
                "badge": "Le plus choisi",
                "recommande": True,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Essentiel",
                    "Comptes agents",
                    "Comptes propriétaires",
                    "Gestion des propriétaires",
                    "Gestion des locataires",
                    "Gestion des bâtiments",
                    "Gestion des logements",
                    "Contrats PDF",
                    "Documents automatiques",
                    "Suivi des loyers",
                    "Suivi des paiements",
                    "Tableau de bord financier",
                    "Notifications automatiques",
                    "Rapports mensuels",
                    "Gestion des dépenses",
                ],
            },

            "premium": {
                "nom": "Premium",
                "prix": 16000,
                "devise": "CAD",
                "delai": "13 à 20 semaines",
                "badge": "Gestion complète",
                "recommande": False,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Professionnel",
                    "Gestion de plusieurs agences",
                    "Application mobile ou PWA",
                    "Portail propriétaire",
                    "Portail locataire",
                    "Portail employé",
                    "Signature électronique",
                    "Demandes de maintenance",
                    "Gestion des interventions",
                    "Comptabilité avancée",
                    "Rapports financiers avancés",
                    "Gestion des centres commerciaux",
                    "Gestion des contrats commerciaux",
                    "Automatisations personnalisées",
                    "Intégrations externes",
                ],
            },
        },
    },

    # ============================================================
    # 6. APPLICATION SUR MESURE
    # ============================================================

    "sur_mesure": {
        "nom": "Application sur mesure",
        "nom_court": "Sur mesure",
        "icone": "fa-code",
        "couleur": "#16a58d",

        "description": (
            "Une solution conçue spécialement selon votre métier, "
            "vos opérations, vos utilisateurs et vos objectifs."
        ),

        "public": (
            "Entreprises, organismes, startups, associations "
            "et projets innovants"
        ),

        "prix_depart": 4000,

        "forfaits": {

            "essentiel": {
                "nom": "Prototype",
                "prix": 9000,
                "devise": "CAD",
                "delai": "6 à 10 semaines",
                "badge": "Valider l’idée",
                "recommande": False,

                "fonctionnalites": [
                    "Analyse du besoin",
                    "Étude des utilisateurs",
                    "Définition des fonctionnalités principales",
                    "Maquettes UI/UX",
                    "Design responsive",
                    "Comptes utilisateurs",
                    "Administration",
                    "Fonctions principales",
                    "Version web responsive",
                    "Tests essentiels",
                    "Mise en ligne",
                    "Documentation simple",
                ],
            },

            "professionnel": {
                "nom": "Professionnel",
                "prix": 19000,
                "devise": "CAD",
                "delai": "10 à 18 semaines",
                "badge": "Produit complet",
                "recommande": True,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du prototype",
                    "Architecture personnalisée",
                    "Base de données avancée",
                    "Paiements ou abonnements",
                    "Documents PDF automatiques",
                    "Emails automatiques",
                    "Rôles et permissions",
                    "Tableau de bord",
                    "Rapports et statistiques",
                    "API pour application mobile",
                    "Sécurité renforcée",
                    "Optimisation des performances",
                    "Tests avancés",
                    "Formation à l’utilisation",
                ],
            },

            "premium": {
                "nom": "Entreprise",
                "prix": 50000,
                "devise": "CAD",
                "delai": "Selon le projet",
                "badge": "Solution entreprise",
                "recommande": False,

                "fonctionnalites": [
                    "Toutes les fonctionnalités du forfait Professionnel",
                    "Application web complète",
                    "Application Android",
                    "Application iOS",
                    "Intelligence artificielle selon le besoin",
                    "Assistant intelligent",
                    "Automatisations avancées",
                    "Intégrations avec services externes",
                    "Architecture haute disponibilité",
                    "Gestion d’un grand nombre d’utilisateurs",
                    "Rapports avancés",
                    "Sécurité avancée",
                    "Accompagnement au lancement",
                    "Formation de l’équipe",
                    "Maintenance évolutive",
                    "Support technique prioritaire",
                ],
            },
        },
    },
}


# ================================================================
# FONCTIONS UTILITAIRES
# ================================================================


def obtenir_application(code_application):
    """
    Retourne une catégorie d’application.

    Exemple :

        application = obtenir_application("restaurant")
    """

    return CATALOGUE_APPLICATIONS.get(code_application)


def obtenir_forfait(code_application, code_forfait):
    """
    Retourne un forfait précis pour une catégorie.

    Exemple :

        forfait = obtenir_forfait(
            "ecommerce",
            "professionnel",
        )
    """

    application = obtenir_application(code_application)

    if not application:
        return None

    return application.get(
        "forfaits",
        {},
    ).get(code_forfait)


def obtenir_offre_complete(code_application, code_forfait):
    """
    Retourne toutes les informations d’une offre sélectionnée.
    """

    application = obtenir_application(code_application)

    forfait = obtenir_forfait(
        code_application,
        code_forfait,
    )

    if not application or not forfait:
        return None

    return {
        "code_application": code_application,
        "nom_application": application["nom"],
        "nom_court": application.get(
            "nom_court",
            application["nom"],
        ),
        "icone": application.get(
            "icone",
            "fa-code",
        ),
        "couleur": application.get(
            "couleur",
            "#16a58d",
        ),
        "description": application.get(
            "description",
            "",
        ),
        "public": application.get(
            "public",
            "",
        ),
        "code_forfait": code_forfait,
        "nom_forfait": forfait["nom"],
        "prix": forfait["prix"],
        "devise": forfait.get(
            "devise",
            "CAD",
        ),
        "delai": forfait["delai"],
        "badge": forfait.get(
            "badge",
            forfait["nom"],
        ),
        "recommande": forfait.get(
            "recommande",
            False,
        ),
        "fonctionnalites": forfait.get(
            "fonctionnalites",
            [],
        ),
    }


def obtenir_choix_applications():
    """
    Retourne les catégories pour un formulaire Django.
    """

    return [
        (
            code_application,
            application["nom"],
        )
        for code_application, application
        in CATALOGUE_APPLICATIONS.items()
    ]


def obtenir_choix_forfaits():
    """
    Retourne les niveaux de qualité disponibles.
    """

    return [
        ("essentiel", "Essentiel"),
        ("professionnel", "Professionnel"),
        ("premium", "Premium"),
    ]


def obtenir_prix_depart(code_application):
    """
    Retourne le prix de départ d’une catégorie.
    """

    application = obtenir_application(code_application)

    if not application:
        return None

    prix_depart = application.get("prix_depart")

    if prix_depart is not None:
        return prix_depart

    forfaits = application.get(
        "forfaits",
        {},
    )

    prix = [
        forfait.get("prix")
        for forfait in forfaits.values()
        if forfait.get("prix") is not None
    ]

    if not prix:
        return None

    return min(prix)


def application_existe(code_application):
    """
    Vérifie si une catégorie existe.
    """

    return code_application in CATALOGUE_APPLICATIONS


def forfait_existe(code_application, code_forfait):
    """
    Vérifie si un forfait existe dans une catégorie.
    """

    return obtenir_forfait(
        code_application,
        code_forfait,
    ) is not None


__all__ = [
    "CATALOGUE_APPLICATIONS",
    "obtenir_application",
    "obtenir_forfait",
    "obtenir_offre_complete",
    "obtenir_choix_applications",
    "obtenir_choix_forfaits",
    "obtenir_prix_depart",
    "application_existe",
    "forfait_existe",
]