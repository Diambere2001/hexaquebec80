from django.contrib import admin
from .models import Product, Order, Announcement, PortfolioItem
from .models import ContactMessage
from django.utils import timezone
from .models import Client, MessageClient
from .models import MessageClient, RendezVous, Partenaire
from django.utils.html import format_html
from .models import VideoAnnonce, Affiche
from .models import Panier, PanierItem
from .models import ProfilStagiaire
from django.contrib.auth.admin import UserAdmin
from .models import CompteStagiaire

from .models import Stagiairelogin
from django.utils.html import format_html
from .forms import ProfilStagiaireForm 


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "quality", "published", "stock", "likes_count")
    list_filter = ("published", "quality")
    search_fields = ("title", "description")
    actions = ["publish_products"]

    # 👉 ICI : on ajoute likes_count
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"

    def publish_products(self, request, queryset):
        for product in queryset:
            product.publish()
        self.message_user(request, "Les produits sélectionnés ont été publiés avec succès.")
# -----------------------
# ADMIN : Commande
# -----------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "nom",
        "prenom",
        "product",
        "total",
        "payment_status",
        "adresse_courte",
        "date_created",
    )

    search_fields = (
        "nom",
        "prenom",
        "courriel",
        "telephone",
        "code",
    )

    list_filter = (
        "paid",
        "date_created",
        "product",
    )

    ordering = ("-date_created",)

    list_display_links = (
        "code",
        "nom",
        "prenom",
    )

    list_per_page = 25

    fields = (
        "code",
        "product",

        "nom",
        "prenom",
        "courriel",
        "telephone",

        "adresse",

        "price",
        "tps",
        "tvq",
        "total",

        "payment_status",
        "stripe_payment_id",

        "date_created",
    )

    readonly_fields = (
        "code",
        "price",
        "tps",
        "tvq",
        "total",
        "payment_status",
        "stripe_payment_id",
        "date_created",
    )

    # Badge paiement couleur
    def payment_status(self, obj):
        if obj.paid:
            return format_html(
                '<span style="color:white;background:green;padding:4px 8px;border-radius:5px;">PAYÉ</span>'
            )
        return format_html(
            '<span style="color:white;background:red;padding:4px 8px;border-radius:5px;">NON PAYÉ</span>'
        )

    payment_status.short_description = "Paiement"

    # Adresse courte
    def adresse_courte(self, obj):
        return obj.adresse[:40] + "..." if len(obj.adresse) > 40 else obj.adresse

    adresse_courte.short_description = "Adresse livraison"
# -----------------------
# ADMIN : Annonce
# -----------------------

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'published_at', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'content')
    actions = ['publish_selected']

    def publish_selected(self, request, queryset):
        for annonce in queryset:
            annonce.publish()
        self.message_user(request, "Les annonces sélectionnées ont été publiées avec succès.")
    publish_selected.short_description = "Publier les annonces sélectionnées"
# -----------------------
# ADMIN : Portfolio
# -----------------------
@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "description")





@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'telephone', 'created_at', 'seen')
    list_filter = ('seen', 'created_at')
    search_fields = ('prenom', 'nom', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    # Optionnel : afficher les messages non lus en haut
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('seen', '-created_at')

    # Changer l’état "vu" directement depuis la liste admin
    actions = ['mark_as_seen']

    def mark_as_seen(self, request, queryset):
        updated = queryset.update(seen=True)
        self.message_user(request, f"{updated} message(s) marqué(s) comme lu(s).")
    mark_as_seen.short_description = "Marquer comme lu"


# ===========================
# ADMIN : Client
# ===========================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("entreprise", "contact", "numero_client", "adresse", "user", "photo_preview")
    search_fields = ("entreprise", "contact", "numero_client")
    list_filter = ("entreprise",)
    ordering = ("entreprise",)

    # Fonction pour afficher un aperçu de la photo
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:50px; height:50px; border-radius:50%"/>', obj.photo.url)
        return "-"
    photo_preview.short_description = "Photo"

@admin.register(MessageClient)
class MessageClientAdmin(admin.ModelAdmin):
    list_display = ("client", "expediteur", "date", "short_message", "has_reply")
    search_fields = ("client__nom", "message", "expediteur__username")
    list_filter = ("date",)

    readonly_fields = ("date",)

    fields = ("client", "expediteur", "message", "image", "fichier", "reponse", "date")

    def short_message(self, obj):
        return obj.message[:50]

    def has_reply(self, obj):
        return bool(obj.reponse)

    has_reply.boolean = True

from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("nom", "prix", "description")
    search_fields = ("nom",)





@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ("client", "date", "heure", "service", "statut")  # Colonnes affichées
    list_filter = ("service", "statut", "date")  # Filtres sur le côté
    search_fields = ("client__user__username", "client__user__email")  # Recherche sur email et username
    ordering = ("-date", "heure")  # Tri par date décroissante puis heure

@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ("client", "nom_entreprise", "telephone", "statut", "logo_preview")
    search_fields = ("nom_entreprise", "client__email")
    list_filter = ("statut",)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;">', obj.logo.url)
        return "—"

    logo_preview.short_description = "Logo"


from .models import CommentPro

@admin.register(CommentPro)
class CommentProAdmin(admin.ModelAdmin):
    list_display = ('short_comment', 'note_display', 'date')
    ordering = ('-date',)

    def short_comment(self, obj):
        # Raccourcir le commentaire dans l'admin
        return (obj.commentaire[:50] + "...") if len(obj.commentaire) > 50 else obj.commentaire
    short_comment.short_description = "Commentaire"

    def note_display(self, obj):
        return "⭐" * obj.note
    note_display.short_description = "Note"





admin.site.register(VideoAnnonce)
admin.site.register(Affiche)


class PanierItemInline(admin.TabularInline):
    model = PanierItem
    extra = 0
    readonly_fields = ('produit', 'quantite', 'total_item')

    def total_item(self, obj):
        return obj.total()
    total_item.short_description = "Total"


# 🔹 Admin Panier
@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'created_at', 'total_panier')
    search_fields = ('session_id',)
    list_filter = ('created_at',)
    inlines = [PanierItemInline]

    def total_panier(self, obj):
        return obj.total()
    total_panier.short_description = "Total panier"


# 🔹 Admin PanierItem
@admin.register(PanierItem)
class PanierItemAdmin(admin.ModelAdmin):
    list_display = ('panier', 'produit', 'quantite', 'total_item')
    list_filter = ('panier',)
    search_fields = ('produit__title',)

    def total_item(self, obj):
        return obj.total()
    total_item.short_description = "Total"





from .models import Stagiaire


@admin.register(Stagiaire)
class StagiaireAdmin(admin.ModelAdmin):

    # 📋 Colonnes affichées
    list_display = (
        'nom',
        'email',
        'specialite',
        'niveau',
        'programme',
        'date_debut',
        'voir_cv',
        'voir_acte',
        'commentaire_preview',  # Aperçu du commentaire
    )

    # 🔍 Recherche
    search_fields = ('nom', 'email', 'specialite', 'programme', 'commentaire')

    # 🎯 Filtres
    list_filter = ('niveau', 'specialite', 'date_debut')

    # 📅 Organisation du formulaire admin
    fieldsets = (
        ("👤 Informations personnelles", {
            'fields': ('nom', 'email', 'code')
        }),
        ("🎓 Formation", {
            'fields': ('specialite', 'niveau', 'programme', 'date_debut')
        }),
        ("📄 Documents", {
            'fields': ('cv', 'acte_naissance', 'lettre_convention')
        }),
        ("🧾 Naissance", {
            'fields': ('date_naissance', 'lieu_naissance')
        }),
        ("📝 Notes & Commentaires", {
            'fields': ('note', 'commentaire')
        }),
        ("📸 Profil", {
            'fields': ('photo',)
        }),
    )

    # 📎 Aperçu CV
    def voir_cv(self, obj):
        if obj.cv:
            return f'<a href="{obj.cv.url}" target="_blank">📄 Voir CV</a>'
        return "❌"
    voir_cv.allow_tags = True
    voir_cv.short_description = "CV"

    # 📎 Aperçu acte de naissance
    def voir_acte(self, obj):
        if obj.acte_naissance:
            return f'<a href="{obj.acte_naissance.url}" target="_blank">📜 Voir</a>'
        return "❌"
    voir_acte.allow_tags = True
    voir_acte.short_description = "Acte"

    # 📝 Aperçu commentaire dans la liste
    def commentaire_preview(self, obj):
        return obj.commentaire[:30] + "..." if obj.commentaire else "—"
    commentaire_preview.short_description = "Commentaire"

    # ⚠️ IMPORTANT pour HTML
    def get_queryset(self, request):
        return super().get_queryset(request)
    
@admin.register(ProfilStagiaire)
class ProfilStagiaireAdmin(admin.ModelAdmin):

    # 📊 LISTE
    list_display = (
        "stagiaire",
        "code_stagiaire",
        "responsable",
        "date_debut",
        "date_fin",
        "stage_valide",
        "projet_valide",
        "reponse_rdv",
        "voir_attestation",
    )

    # 🔍 RECHERCHE
    search_fields = (
        "stagiaire__nom",
        "code_stagiaire",
        "responsable",
    )

    # 🧠 FILTRES
    list_filter = (
        "stage_valide",
        "projet_valide",
        "reponse_rdv",
        "pays_naissance",
        "date_debut",
        "date_fin",
    )

    # ✏️ FORMULAIRE
    fieldsets = (

        ("👤 Informations stagiaire", {
            "fields": (
                "stagiaire",
                "code_stagiaire",
                "photo_preview",
                "photo",
            )
        }),

        ("📄 Documents", {
            "fields": (
                "cv",
                "acte_naissance",
            )
        }),

        ("🌍 Naissance", {
            "fields": (
                "date_naissance",
                "lieu_naissance",
                "pays_naissance",
            )
        }),

        ("👨‍🏫 Responsable & Signature", {
            "fields": (
                 "responsable",

        # ✍️ SIGNATURE
               "signature_preview",
                "signature_data",

            # 💬 MESSAGERIE ADMIN → STAGIAIRE
                "message_responsable",

        # 💬 RÉPONSE ADMIN → STAGIAIRE (nouveau)
                "reponse_admin",
                "message_stagiaire",
            )
        }),

        ("📅 Rendez-vous", {
            "fields": (
                "date_rdv",
                "statut_rdv",
                "reponse_rdv",
            )
        }),

        ("📘 Projet", {
            "fields": (
                "titre_projet",
                "projet_fichier",
                "projet_valide",
            )
        }),

        ("📄 Attestation", {
            "fields": (
                "stage_valide",
                "attestation",
                "voir_attestation",
            )
        }),

        ("📅 Période du stage", {
            "fields": (
                "date_debut",
                "date_fin",
            )
        }),
    )

    # 🔒 READONLY
    readonly_fields = (
        "code_stagiaire",
        "attestation",
        "voir_attestation",
        "photo_preview",
        "signature_preview",
    )

    # ⚡ ACTIONS
    actions = ["valider_stage", "valider_projet"]

    # 👁️ PHOTO
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="80" style="border-radius:8px;" />',
                obj.photo.url
            )
        return "Aucune photo"
    photo_preview.short_description = "Aperçu photo"

    # ✍️ SIGNATURE
    def signature_preview(self, obj):
        if obj.signature_data:
            try:
                return format_html(
                    '<img src="{}" width="150" style="border:1px solid #ccc; border-radius:4px;" />',
                    obj.signature_data
                )
            except:
                return format_html("<span style='color:red;'>Erreur signature</span>")
        return format_html("<span style='color:gray;'>Signature non définie</span>")
    signature_preview.short_description = "Aperçu signature"

    # 📄 VOIR PDF
    def voir_attestation(self, obj):
        if obj.attestation:
            return format_html(
                '<a class="button" href="{}" target="_blank">📄 Télécharger PDF</a>',
                obj.attestation.url
            )
        return "Pas encore générée"
    voir_attestation.short_description = "Attestation"

    # 🔥 VALIDER STAGE
    def valider_stage(self, request, queryset):
        for profil in queryset:
            profil.stage_valide = True

            # ✅ IMPORTANT : auto date fin
            if not profil.date_fin:
                profil.date_fin = timezone.now().date()

            # 🔁 regen PDF
            profil.attestation = None
            profil.save()

        self.message_user(request, "✅ Stage validé + attestation générée")
    valider_stage.short_description = "Valider stage + générer attestation"

    # 🔥 VALIDER PROJET
    def valider_projet(self, request, queryset):
        queryset.update(projet_valide=True)
        self.message_user(request, "📘 Projet validé")
    valider_projet.short_description = "Valider projet"


class CompteStagiaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'code_stagiaire', 'autorise', 'is_admin')
    list_filter = ('autorise', 'is_admin')
    search_fields = ('nom', 'email', 'code_stagiaire')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'code_stagiaire', 'nom', 'password')}),
        ('Permissions', {'fields': ('autorise', 'is_admin')}),
    )

admin.site.register(CompteStagiaire, CompteStagiaireAdmin)




from django.contrib import admin
from .models import Stagiairelogin


@admin.register(Stagiairelogin)
class StagiaireloginAdmin(admin.ModelAdmin):
    list_display = ('email', 'accepte', 'refuse', 'date_creation')
    list_filter = ('accepte', 'refuse')
    search_fields = ('email',)

    actions = ['accepter_demandes', 'refuser_demandes']

    # ✅ ACTION : ACCEPTER
    def accepter_demandes(self, request, queryset):
        count = 0

        for stagiaire in queryset:
            # éviter double traitement
            if not stagiaire.accepte and not stagiaire.refuse:
                stagiaire.generer_code()  # 🔐 code
                stagiaire.accepte = True
                stagiaire.refuse = False
                stagiaire.save()

                # 📧 email
                stagiaire.envoyer_email_acceptation()

                count += 1

        self.message_user(
            request,
            f"✅ {count} demande(s) acceptée(s) et email(s) envoyé(s)."
        )

    accepter_demandes.short_description = "✅ Accepter les demandes sélectionnées"

    # ❌ ACTION : REFUSER
    def refuser_demandes(self, request, queryset):
        count = 0

        for stagiaire in queryset:
            # éviter double refus
            if not stagiaire.refuse:
                stagiaire.accepte = False
                stagiaire.refuse = True
                stagiaire.save()

                # 📧 email
                stagiaire.envoyer_email_refus()

                count += 1

        self.message_user(
            request,
            f"❌ {count} demande(s) refusée(s) et email(s) envoyé(s)."
        )

    refuser_demandes.short_description = "❌ Refuser les demandes sélectionnées"





from .models import Devis


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):

    # Colonnes affichées dans la liste
    list_display = ("nom", "email", "service", "type_projet", "date")

    # Filtres à droite
    list_filter = ("service", "date")

    # Barre de recherche
    search_fields = ("nom", "email", "type_projet", "description")

    # Ordre
    ordering = ("-date",)

    # Champs en lecture seule
    readonly_fields = ("date",)

    # Organisation du formulaire admin
    fieldsets = (
        ("Informations client", {
            "fields": ("nom", "email")
        }),
        ("Projet", {
            "fields": ("service", "type_projet", "description", "fichier")
        }),
        ("Date", {
            "fields": ("date",)
        }),
    )

def fichier_link(self, obj):
    if obj.fichier:
        return f'<a href="{obj.fichier.url}" target="_blank">Voir fichier</a>'
    return "-"
fichier_link.allow_tags = True
fichier_link.short_description = "Fichier"




from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_id', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    ordering = ('-created_at',)




from django.contrib import admin
from .models import Facture, LigneFacture


# 👉 Afficher les lignes directement dans la facture
class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1  # nombre de lignes vides affichées
    fields = ('produit', 'quantite', 'prix_unitaire')
    readonly_fields = ()
    show_change_link = True




# 👉 Inline des lignes de facture
class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1
    fields = ('produit', 'quantite', 'prix_unitaire')
    show_change_link = True


# 👉 Admin Facture corrigé
@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):

    list_display = (
        'numero',
        'vendeur_nom',
        'acheteur_nom',
        'date',
        'created_at',
        'total_facture_display'
    )

    search_fields = (
        'numero',
        'vendeur_nom',
        'acheteur_nom'
    )

    list_filter = (
        'date',
        'created_at'
    )

    ordering = ('-created_at',)

    inlines = [LigneFactureInline]

    readonly_fields = (
        'numero',
        'created_at'
    )

    # 👉 afficher le total dans l'admin
    def total_facture_display(self, obj):
        return obj.total_facture()

    total_facture_display.short_description = "Total facture"


# 👉 Admin LigneFacture (optionnel mais utile)
@admin.register(LigneFacture)
class LigneFactureAdmin(admin.ModelAdmin):
    list_display = ('facture', 'produit', 'quantite', 'prix_unitaire')
    search_fields = ('produit',)