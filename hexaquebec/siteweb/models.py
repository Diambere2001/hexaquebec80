from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import uuid
from decimal import Decimal






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
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)


    def publish(self):
        """Publie le produit sur le site."""
        self.published = True
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def user_has_liked(self, user):
        return self.likes.filter(id=user.id).exists()




# ------------------------
# Modèle : Commande
# ------------------------class Order(models.Model):
class Order(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    adresse = models.TextField()

    telephone = models.CharField(max_length=20, blank=True)

    courriel = models.EmailField()

    date_created = models.DateTimeField(default=timezone.now)

    code = models.CharField(max_length=12, unique=True, editable=False, null=True, blank=True)

    # prix produit
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # taxes Québec
    tps = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tvq = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # total
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
    max_length=20,
    choices=[
        ("pending", "En attente"),
        ("paid", "Payé"),
        ("shipped", "Expédié"),
    ],
    default="pending"
    )

    # paiement
    paid = models.BooleanField(default=False)

    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):

        if not self.code:
            while True:
                new_code = str(uuid.uuid4().int)[:12]
                if not Order.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break

        # calcul prix et taxes
        if self.product:

            self.price = self.product.price

            self.tps = self.price * Decimal('0.05')        # TPS corrigé
            self.tvq = self.price * Decimal('0.09975') 

            self.total = self.price + self.tps + self.tvq

        super().save(*args, **kwargs)

    def __str__(self):
        return f"COMMANDE #{self.code}"

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


class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.user.username}"


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity


class Commentaire(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.email})"





def generate_client_number():
    return "HEX-" + str(random.randint(100000, 999999))

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    entreprise = models.CharField(max_length=150)
    contact = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    numero_client = models.CharField(max_length=20, unique=True, default=generate_client_number)

    def __str__(self):
        return f"{self.entreprise} ({self.numero_client})"


class MessageClient(models.Model):
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    expediteur = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    reponse = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Message de {self.client}"
class RendezVous(models.Model):
    SERVICE_CHOICES = [
        ('commercial', 'Commercial'),
        ('industriel', 'Industriel'),
        ('gouvernemental', 'Gouvernemental'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]

    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.client.user.username} - {self.service} - {self.date} {self.heure}"


class Partenaire(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="partenaires")
    nom_entreprise = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    activite = models.TextField()
    statut = models.CharField(max_length=20, default="En attente")
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)   # ✔ ajouté ici

    def __str__(self):
        return self.nom_entreprise

class Projet(models.Model):
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="projets/")

    def __str__(self):
        return self.titre

class MessageContact(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom} - {self.sujet}"

class Message(models.Model):
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_envoyes")
    destinataire_email = models.EmailField()
    objet = models.CharField(max_length=255)
    contenu = models.TextField()
    fichier = models.FileField(upload_to='documents/', null=True, blank=True)  # <-- nouveau champ
    date_envoi = models.DateTimeField(auto_now_add=True)

class CommentPro(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ➜ Ajouter ceci
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    note = models.PositiveIntegerField(default=5)  # ⭐⭐⭐⭐⭐

    def __str__(self):
        return f"Commentaire du {self.date}"



class VideoAnnonce(models.Model):
    titre = models.CharField(max_length=200)
    video = models.FileField(upload_to="videos_annonces/")
    date_pub = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Affiche(models.Model):
    titre = models.CharField(max_length=200)
    image = models.ImageField(upload_to='affiches/')
    actif = models.BooleanField(default=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre




class Facture(models.Model):

    numero = models.CharField(max_length=20, unique=True)

    vendeur_nom = models.CharField(max_length=200)
    acheteur_nom = models.CharField(max_length=200)

    produit = models.CharField(max_length=200)

    prix = models.DecimalField(max_digits=10, decimal_places=2)

    date = models.DateField()

    
    signature_vendeur = models.TextField(blank=True, null=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.numero
    




class Panier(models.Model):
    session_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def total(self):
        return sum(item.total() for item in self.items.all())

    def __str__(self):
        return f"Panier {self.id} - {self.session_id}"


class PanierItem(models.Model):
    panier = models.ForeignKey(Panier, related_name='items', on_delete=models.CASCADE)
    produit = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def total(self):
        return self.produit.price * self.quantite

    def __str__(self):
        return f"{self.produit.title} x {self.quantite}"