from django.contrib import admin
from .models import Product, Order, Announcement, PortfolioItem
from .models import ContactMessage
from django.utils import timezone
from .models import Client, MessageClient
from .models import MessageClient, RendezVous, Partenaire
from django.utils.html import format_html
from .models import VideoAnnonce, Affiche


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
        "code",        # numéro de commande unique
        "nom",
        "prenom",
        "product",
        "telephone",
        "courriel",
        "date_created",
    )
    search_fields = ("nom", "prenom", "courriel", "product__nom", "code")
    list_filter = ("date_created", "product")
    ordering = ("-date_created",)
    list_display_links = ("code", "nom", "prenom")
    list_per_page = 25
    fields = (
        "code",
        "nom",
        "prenom",
        "courriel",
        "telephone",
        "product",
        "adresse",
        "date_created",
    )
    readonly_fields = ("code", "date_created")  # pour ne pas pouvoir modifier manuellement



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
    list_display = ("entreprise", "contact", "numero_client", "adresse", "user")
    search_fields = ("entreprise", "contact", "numero_client")
    list_filter = ("entreprise",)
    ordering = ("entreprise",)

# ===========================
# ADMIN : MessageClient
# ===========================
@admin.register(MessageClient)
class MessageClientAdmin(admin.ModelAdmin):
    list_display = ("client", "date", "message", "reponse")
    search_fields = ("client__entreprise", "message")
    list_filter = ("date",)
    ordering = ("-date",)


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