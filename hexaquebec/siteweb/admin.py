from django.contrib import admin
from .models import Product, Order, Announcement, PortfolioItem
from .models import ContactMessage
from django.utils import timezone


# -----------------------
# ADMIN : Produit
# -----------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "quality", "published", "stock")
    list_filter = ("published", "quality")
    search_fields = ("title", "description")
    actions = ["publish_products"]

    def publish_products(self, request, queryset):
        for product in queryset:
            product.publish()
        self.message_user(request, "Les produits sélectionnés ont été publiés avec succès.")
    publish_products.short_description = "Publier les produits sélectionnés"


# -----------------------
# ADMIN : Commande
# -----------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "product", "telephone", "courriel", "date_commande")
    search_fields = ("nom", "prenom", "courriel", "product__nom")
    list_filter = ("date_commande", "product")
    ordering = ("-date_commande",)
    list_display_links = ("nom", "prenom")
    list_per_page = 25
    fields = ("nom", "prenom", "courriel", "telephone", "product", "adresse", "date_commande")  # quantite supprimé



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