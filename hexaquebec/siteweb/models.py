from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import uuid
from decimal import Decimal
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.conf import settings





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




import random
from django.db import models
from django.contrib.auth.models import User

def generate_client_number():
    return "HEX-" + str(random.randint(100000, 999999))

# Fonction pour le chemin d'upload
def upload_to_client(instance, filename):
    return f'client_photos/{instance.user.id}/{filename}'

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    entreprise = models.CharField(max_length=150)
    contact = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    numero_client = models.CharField(max_length=20, unique=True, default=generate_client_number)

    # 📷 Photo du client
    photo = models.ImageField(
        upload_to=upload_to_client,  # ✅ fonction normale, pas de lambda
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.entreprise} ({self.numero_client})"

class Service(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom



class MessageClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()
    image = models.ImageField(upload_to="messages/images/", null=True, blank=True)
    fichier = models.FileField(upload_to="messages/files/", null=True, blank=True)

    reponse = models.TextField(blank=True, null=True)  # admin répond ici
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - {self.date}"
    
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

from cloudinary.models import CloudinaryField

class VideoAnnonce(models.Model):
    titre = models.CharField(max_length=200)

    video = CloudinaryField(
        resource_type="video",
        folder="videos_annonces",
        blank=True,
        null=True
    )

    date_pub = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

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

    numero = models.CharField(max_length=20, unique=True, blank=True)

    vendeur_nom = models.CharField(max_length=200)
    acheteur_nom = models.CharField(max_length=200)

    # ✅ NOUVEAU : adresse client
    adresse_client = models.CharField(max_length=255)
    ville_client = models.CharField(max_length=100)
    code_postal_client = models.CharField(max_length=20)
    pays_client = models.CharField(max_length=100, default="Canada")

    date = models.DateField()

    signature_vendeur = models.TextField(blank=True, null=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero:
            last_facture = Facture.objects.order_by('-id').first()

            if last_facture:
                last_num = int(last_facture.numero.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.numero = f"HEX-{new_num:04d}"

        super().save(*args, **kwargs)

    def total_facture(self):
        return sum(ligne.total() for ligne in self.lignes.all())

    def __str__(self):
        return self.numero
    
    
class LigneFacture(models.Model):
    facture = models.ForeignKey(
        Facture,
        on_delete=models.CASCADE,
        related_name='lignes'
    )

    produit = models.CharField(max_length=200)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.produit} x{self.quantite}"





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
    

class Stagiaire(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=10)

    specialite = models.CharField(max_length=100)
    niveau = models.CharField(max_length=50)
    programme = models.TextField(blank=True)

    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(null=True, blank=True)

    # 📄 CV
    cv = models.FileField(upload_to="cv/", null=True, blank=True)

    # 📄 Acte de naissance
    acte_naissance = models.FileField(upload_to="actes/", null=True, blank=True)

    # 📄 Lettre de convention école ✅ NOUVEAU
    lettre_convention = models.FileField(upload_to="conventions/", null=True, blank=True)

    # 📅 Infos naissance
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=150, blank=True)

    # 📸 Photo
    photo = models.ImageField(upload_to="profiles/", null=True, blank=True)

    # 📝 Autres
    note = models.CharField(max_length=50, blank=True)
    commentaire = models.TextField(blank=True)

    def __str__(self):
        return self.nom






import random
import string
import os
from io import BytesIO
import base64

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from cloudinary_storage.storage import RawMediaCloudinaryStorage


import qrcode

class ProfilStagiaire(models.Model):
    stagiaire = models.OneToOneField('Stagiaire', on_delete=models.CASCADE)
    code_stagiaire = models.CharField(max_length=10, unique=True, blank=True)

    cv = models.FileField(upload_to="cv/", null=True, blank=True)
    acte_naissance = models.FileField(upload_to="actes/", null=True, blank=True)
    photo = models.ImageField(upload_to="profiles/", null=True, blank=True)

    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=150, blank=True)
    pays_naissance = models.CharField(max_length=100, blank=True)

    responsable = models.CharField(max_length=150, blank=True)
    signature_data = models.TextField(blank=True, null=True)

    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(null=True, blank=True)

    statut_rdv = models.CharField(
        max_length=20,
        choices=[
            ("aucun", "Aucun"),
            ("en_attente", "En attente"),
            ("accepte", "Accepté"),
            ("refuse", "Refusé"),
        ],
        default="aucun"
    )

    date_rdv = models.DateTimeField(null=True, blank=True)

    reponse_rdv = models.CharField(
        max_length=50,
        choices=[
            ('en_attente','En attente'),
            ('accepte','Accepté'),
            ('refuse','Refusé')
        ],
        default='en_attente'
    )

    titre_projet = models.CharField(max_length=200, blank=True)
    projet_fichier = models.FileField(upload_to="projets/", null=True, blank=True)
    projet_valide = models.BooleanField(default=False)

    attestation = models.FileField(
        upload_to="attestations/",
        null=True,
        blank=True
    )

    stage_valide = models.BooleanField(default=False)

    def generate_code(self):
        if not self.code_stagiaire:
            self.code_stagiaire = "STG-" + ''.join(random.choices(string.digits, k=5))
        return self.code_stagiaire

    def save(self, *args, **kwargs):
        if not self.code_stagiaire:
            self.generate_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stagiaire.nom} - {self.code_stagiaire}"







class AttestationStage(models.Model):

    numero_attestation = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name="Numéro de l’attestation",
    )

    numero_stagiaire = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Numéro du stagiaire",
        help_text="Exemple : STG-12345",
    )

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom",
    )

    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom",
    )

    programme = models.CharField(
        max_length=200,
        verbose_name="Programme ou domaine du stage",
    )

    date_debut = models.DateField(
        verbose_name="Date de début",
    )

    date_fin = models.DateField(
        verbose_name="Date de fin",
    )

    date_delivrance = models.DateField(
        default=timezone.localdate,
        editable=False,
        verbose_name="Date de délivrance",
    )

    lieu_delivrance = models.CharField(
        max_length=150,
        default="Saguenay, Québec, Canada",
        verbose_name="Lieu de délivrance",
    )

    responsable = models.CharField(
        max_length=150,
        default="Diambere Kamara",
        verbose_name="Nom du responsable",
    )

    fonction_responsable = models.CharField(
        max_length=150,
        default="Directeur fondateur",
        verbose_name="Fonction du responsable",
    )

    signature_data = models.TextField(
        verbose_name="Signature électronique",
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attestations_stage_creees",
        verbose_name="Créée par",
    )

    actif = models.BooleanField(
        default=True,
        verbose_name="Attestation active",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification",
    )

    class Meta:
        ordering = [
            "-date_delivrance",
            "-id",
        ]

        verbose_name = "Attestation de stage"
        verbose_name_plural = "Attestations de stage"

    def clean(self):

        super().clean()

        if (
            self.date_debut
            and self.date_fin
            and self.date_fin < self.date_debut
        ):
            raise ValidationError({
                "date_fin": (
                    "La date de fin ne peut pas être "
                    "antérieure à la date de début."
                )
            })

    def generer_numero_attestation(self):

        annee = timezone.localdate().year
        identifiant = uuid.uuid4().hex[:8].upper()

        return f"ATT-{annee}-{identifiant}"

    def save(self, *args, **kwargs):

        if not self.numero_attestation:
            self.numero_attestation = (
                self.generer_numero_attestation()
            )

        super().save(*args, **kwargs)

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}".strip()

    def __str__(self):

        return (
            f"{self.numero_attestation} - "
            f"{self.prenom} {self.nom}"
        )

class DocumentStagiaire(models.Model):
    profil = models.ForeignKey(
        ProfilStagiaire,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    titre = models.CharField(max_length=150)
    fichier = models.FileField(upload_to="documents_stagiaires/")

    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} - {self.profil.stagiaire}"






class CompteStagiaireManager(BaseUserManager):
    def create_user(self, email, code_stagiaire, password=None):
        if not email:
            raise ValueError("L'email est requis")
        if not code_stagiaire:
            raise ValueError("Le code stagiaire est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, code_stagiaire=code_stagiaire)
        user.set_password(password or code_stagiaire)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, code_stagiaire, password=None):
        user = self.create_user(email, code_stagiaire, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CompteStagiaire(AbstractBaseUser):
    email = models.EmailField(unique=True)
    code_stagiaire = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=200)
    autorise = models.BooleanField(default=False)  # Validation admin
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CompteStagiaireManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['code_stagiaire']

    def __str__(self):
        return f"{self.nom} ({self.code_stagiaire})"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin







    



import random
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

class Stagiairelogin(models.Model):
    stagiaire = models.OneToOneField(Stagiaire, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    accepte = models.BooleanField(default=False)
    refuse = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def generer_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()

    def envoyer_email_acceptation(self):
        login_url = settings.SITE_URL + reverse('login_stagiaire')

        subject = "Demande de stage acceptée - HexaQuébec"
        message = f"""
Bonjour {self.stagiaire.nom},

Votre demande de stage a été acceptée ✅

Email : {self.email}
Code : {self.code}

Connexion : {login_url}

Merci.
"""
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    def envoyer_email_refus(self):
        subject = "Demande refusée - HexaQuébec"
        message = f"""
Bonjour {self.stagiaire.nom},

Votre demande de stage a été refusée ❌

Merci.
"""
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    def __str__(self):
        return self.email
    





class Devis(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    service = models.CharField(max_length=100)
    type_projet = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to="devis/", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)




from django.db import models

class PaiementClient(models.Model):
    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('non_paye', 'Non payé'),
    ]

    nom_client = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255)
    telephone = models.CharField(max_length=30)
    residence = models.CharField(max_length=255, blank=True, null=True)

    titre_projet = models.CharField(max_length=255)

    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='non_paye')

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_client} - {self.montant} - {self.statut}"
    






class Projet(models.Model):

    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('encours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    nom_projet = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    date_creation = models.DateField(default=timezone.now)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='disponible'
    )

    technologie = models.CharField(max_length=200, blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    image = models.ImageField(
        upload_to='projets/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nom_projet
    


class PresenceStagiaire(models.Model):

    profil = models.ForeignKey(
        "ProfilStagiaire",
        on_delete=models.CASCADE,
        related_name="presences"
    )

    # DATE
    date = models.DateField(auto_now_add=True)

    # HORAIRE
    horaire_entree = models.TimeField(
        null=True,
        blank=True
    )

    pause_repas = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    horaire_sortie = models.TimeField(
        null=True,
        blank=True
    )

    # POINTAGE
    pointage_entree = models.TimeField(
        null=True,
        blank=True
    )

    pointage_sortie = models.TimeField(
        null=True,
        blank=True
    )

    # ABSENCE
    absent = models.BooleanField(default=False)

    raison_absence = models.TextField(
        blank=True,
        null=True
    )

    # NOTES
    note_admin = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.profil} - {self.date}"
    







class RapportMensuel(models.Model):

    TYPE_CHOICES = (
        ('revenu', 'Revenu'),
        ('depense', 'Dépense'),
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    description = models.CharField(
        max_length=255
    )

    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.type} - {self.montant}$"




class MessageStagiaire(models.Model):

    profil = models.ForeignKey(
        ProfilStagiaire,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    auteur = models.CharField(
        max_length=20,
        choices=[
            ("stagiaire", "Stagiaire"),
            ("admin", "Administration"),
        ]
    )

    message = models.TextField()

    date = models.DateTimeField(
        auto_now_add=True
    )

    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.auteur} - {self.profil}"



class GroupeStagiaire(models.Model):
    nom = models.CharField(max_length=100, default="Groupe Stagiaires")
    stagiaires = models.ManyToManyField("ProfilStagiaire", blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class MessageGroupeStagiaire(models.Model):
    groupe = models.ForeignKey(
        GroupeStagiaire,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField(blank=True)

    fichier = models.FileField(
        upload_to="groupe_stagiaires/",
        blank=True,
        null=True
    )

    lu = models.BooleanField(default=False)

    date = models.DateTimeField(auto_now_add=True)

    supprime = models.BooleanField(default=False)
    supprime_par = models.CharField(max_length=150, blank=True, null=True)
    date_suppression = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.auteur.username}"
    


class ReactionMessage(models.Model):
    message = models.ForeignKey(
        MessageGroupeStagiaire,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    emoji = models.CharField(max_length=10)



class MessageLu(models.Model):
    message = models.ForeignKey(
        MessageGroupeStagiaire,
        on_delete=models.CASCADE
    )

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    date_lecture = models.DateTimeField(auto_now_add=True)