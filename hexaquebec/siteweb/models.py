from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# ------------------------
# Modèle : Produit
# ------------------------

class Product(models.Model):
    QUALITY_CHOICES = [
        ("neuf", "Neuf"),
        ("reconditionne", "Reconditionné"),
        ("occasion", "Occasion"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def publish(self):
        """Publie le produit sur le site."""
        self.published = True
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title


# ------------------------
# Modèle : Commande
# ------------------------
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    courriel = models.EmailField()
    date_commande = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Commande #{self.id} - {self.nom} {self.prenom} ({self.product.title})"



# ------------------------
# Modèle : Annonce
# ------------------------
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='annonces/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def publish(self):
        self.published = True
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title


# ------------------------
# Modèle : Réalisation (Portfolio)
# ------------------------
class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="portfolio/", blank=True, null=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)  # si tu veux suivre si le message a été lu

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.email}"


class CartItem(models.Model):
    produit = models.ForeignKey('Product', on_delete=models.CASCADE)  # Utiliser Product ici
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.produit.prix * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.produit.titre}"



class Commentaire(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.email})"