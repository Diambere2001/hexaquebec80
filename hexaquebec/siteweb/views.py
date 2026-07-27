from decimal import Decimal

from reportlab.platypus import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os, json
from dotenv import load_dotenv

import stripe
import openai
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from .models import Product, Order
from reportlab.lib.pagesizes import A4  # <-- Ajoute ceci
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.views.decorators.http import require_POST
import mimetypes  # <-- Ajoute cette ligne
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem
from .models import PaiementClient



from .models import (
    Product,
    Announcement,
    PortfolioItem,
    ContactMessage,
    CartItem,
    Commentaire,
    DemandeApplication,
)
from .forms import ContactForm, OrderForm, UrgenceForm
from django.contrib.auth import authenticate, login, logout
from .models import Client
from .forms import ClientRegisterForm, ClientLoginForm, MessageClientForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Client, MessageClient, RendezVous, Partenaire,Service
from .forms import MessageForm, RendezVousForm, PartenaireForm
from .forms import AdminSendMailForm, ContactClientForm
from .models import MessageContact
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Client, Message
from .forms import MessageForm
from django.template.loader import get_template, render_to_string  
from django.core.mail import EmailMessage
from .catalogue_applications import (
    CATALOGUE_APPLICATIONS,
    obtenir_offre_complete,
)
from .forms import DemandeApplicationForm



# 🔹 Charger la clé API depuis .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def home(request):
    if not OPENAI_API_KEY:
        return HttpResponse("Service temporairement indisponible", status=503)

    return HttpResponse("Site HexaQuebec en ligne ✅")


# ===================== CHATBOT =====================
@csrf_exempt
def chatbot_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Message vide reçu."}, status=400)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "Tu es l’assistant virtuel professionnel de HexaQuébec. "
                    "Tu réponds toujours en français et aides sur les services, produits et informations générales."
                )},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        bot_reply = completion.choices[0].message['content'].strip()
        return JsonResponse({"reply": bot_reply})
    except Exception as e:
        print("Erreur API:", e)
        return JsonResponse({"error": str(e)}, status=500)

from .models import VideoAnnonce, Affiche
# ===================== HOME =====================
def home_view(request):
    annonces = Announcement.objects.filter(
        published=True,
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:5]

    products = Product.objects.filter(published=True)
    portfolio = PortfolioItem.objects.all()
    partenaires = Partenaire.objects.all()

    # 🔥 VIDEO PUB
    videos = VideoAnnonce.objects.all().order_by('-date_pub')[:1]

    # 🔥 AFFICHES PUB
    affiches = Affiche.objects.filter(actif=True).order_by('-date_pub')[:3]

    form = UrgenceForm()

    services = [
        {
            'title': 'Développement Web',
            'description': 'Création de sites web modernes...',
            'icon': 'fa-solid fa-laptop-code',
            'image': 'images/dev.jpg'
        },
        {
            'title': 'Maintenance Informatique',
            'description': 'Assistance, mise à jour...',
            'icon': 'fa-solid fa-tools',
            'image': 'images/maintenance.jpg'
        },
    ]

    context = {
        'annonces': annonces,
        'products': products,
        'portfolio': portfolio,
        'services': services,
        'form': form,
        'partenaires': partenaires,

        # 🔥 AJOUTS
        'videos': videos,
        'affiches': affiches,
    }

    return render(request, 'home.html', context)


# ===================== ANNOUNCEMENTS =====================
def annonce_detail(request, annonce_id):
    annonce = get_object_or_404(Announcement, id=annonce_id)
    return render(request, 'annonce_detail.html', {'annonce': annonce})


def annonces_list(request):
    annonces = Announcement.objects.filter(published=True).order_by('-published_at')
    return render(request, 'annonces.html', {'annonces': annonces})


# ===================== CONTACT =====================
def contact_view(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        email = request.POST.get("email", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        message = request.POST.get("message", "").strip()

        if not nom or not email or not telephone or not message:
            messages.error(request, "⚠️ Tous les champs sont obligatoires.")
            return redirect("contact")

        ContactMessage.objects.create(
            prenom=nom.split()[0],
            nom=" ".join(nom.split()[1:]) if len(nom.split()) > 1 else "",
            email=email,
            telephone=telephone,
            message=message,
        )

        try:
            send_mail(
                subject=f"Nouveau message de {nom}",
                message=f"Nom: {nom}\nEmail: {email}\nTéléphone: {telephone}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["hexaquebec80@gmail.com"],
                fail_silently=False,
            )
        except Exception:
            messages.warning(request, "Message enregistré mais l’envoi du courriel a échoué.")

        messages.success(request, "✅ Votre message a été envoyé avec succès !")
        return redirect("contact")

    return render(request, "contact.html")


# ===================== PORTFOLIO =====================
def portfolio_list(request):
    # Exemple : tu peux passer une liste de projets si besoin
    projets = [
    {'id': 1, 'titre': 'Projet 1', 'description': 'Description courte du projet 1', 'image': 'images/projet1.jpg'},
    {'id': 2, 'titre': 'Projet 2', 'description': 'Description courte du projet 2', 'image': 'images/projet2.jpg'},
    {'id': 3, 'titre': 'Projet 3', 'description': 'Description courte du projet 3', 'image': 'images/projet3.jpg'},
    {'id': 4, 'titre': 'Projet 4', 'description': 'Description courte du projet 4', 'image': 'images/projet4.jpg'},
    {'id': 5, 'titre': 'Projet 5', 'description': 'Description courte du projet 5', 'image': 'images/projet5.jpg'},
    {'id': 6, 'titre': 'Projet 6', 'description': 'Description courte du projet 6', 'image': 'images/projet6.jpg'},
]

    return render(request, 'portfolio.html', {'projets': projets})
from .models import Projet


def detail_projet(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    return render(request, 'detail.html', {'projet': projet})
# ===================== SERVICES =====================
def services(request):
    return render(request, 'nos_services.html')


def services_view(request):
    return render(request, 'services_detail.html')


from .models import Product, CommentPro 
def produits_list(request):
    # 🔹 Récupérer seulement les produits publiés
    produits = Product.objects.filter(published=True)

    # 🔹 Gestion de l’envoi d’un commentaire
    if request.method == "POST":
        contenu = request.POST.get("commentaire")
        if contenu:
            CommentPro.objects.create(
                commentaire=contenu,
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, "Votre message a été publié !")
            return redirect("produits_list")  # Évite les resoumissions POST

    # 🔹 Récupérer tous les commentaires récents
    commentaires = CommentPro.objects.all().order_by('-date')

    return render(request, "produits_list.html", {
        "produits": produits,
        "commentaires": commentaires,
    })


def product_detail(request, produit_id):
    produit = get_object_or_404(Product, id=produit_id)

    order = None
    barcode_base64 = None

    if request.user.is_authenticated:
        order = Order.objects.filter(courriel=request.user.email).last()

        if order:
            from io import BytesIO
            import base64
            import barcode
            from barcode.writer import ImageWriter

            CODE128 = barcode.get_barcode_class('code128')
            barcode_image = CODE128(str(order.id), writer=ImageWriter())
            buffer = BytesIO()
            barcode_image.write(buffer)
            barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    context = {
        'produit': produit,
        'produits': Product.objects.exclude(id=produit.id)[:4],
        'order': order,
        'barcode_base64': barcode_base64,
    }

    return render(request, 'product_detail.html', context)


# ===================== STRIPE =====================
def paiement_stripe(request, produit_id):
    produit = get_object_or_404(Product, id=produit_id)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "cad",
                "product_data": {"name": produit.titre},
                "unit_amount": int(produit.prix * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri("/paiement/success/"),
        cancel_url=request.build_absolute_uri("/paiement/cancel/"),
    )
    return redirect(session.url, code=303)


from django.core.mail import EmailMessage






def paiement_cancel(request):
    return render(request, "cancel.html")


def paiement_panier(request):
    items = CartItem.objects.all()
    line_items = []
    for item in items:
        line_items.append({
            "price_data": {
                "currency": "cad",
                "product_data": {"name": item.produit.titre},
                "unit_amount": int(item.produit.prix * 100),
            },
            "quantity": item.quantity,
        })
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=request.build_absolute_uri("/paiement/success/"),
        cancel_url=request.build_absolute_uri("/paiement/cancel/"),
    )
    return redirect(session.url, code=303)


# ===================== COMMANDES =====================



def passer_commande(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        adresse = request.POST.get("adresse")
        telephone = request.POST.get("telephone")
        courriel = request.POST.get("courriel")

        # ✅ Validation simple obligatoire
        if not all([nom, prenom, adresse, telephone, courriel]):
            return render(request, "passer_commande.html", {
                "product": product,
                "error": "Veuillez remplir tous les champs."
            })

        # Vérification email simple
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", courriel):
            return render(request, "passer_commande.html", {
                "product": product,
                "error": "Adresse e-mail invalide."
            })

        # Créer la commande
        order = Order.objects.create(
            product=product,
            nom=nom,
            prenom=prenom,
            adresse=adresse,
            telephone=telephone,
            courriel=courriel
        )

        # Redirection vers checkout avec product_id
        return redirect('checkout', product_id=product.id)

    return render(request, "passer_commande.html", {"product": product})
    







# ===================== URGENCE AJAX =====================
def urgence_view(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = UrgenceForm(request.POST)
        if form.is_valid():
            # form.save() si tu veux sauvegarder
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# ===================== COMMENTAIRES =====================
@csrf_exempt
def submit_commentaire(request):
    if request.method == "POST":
        data = json.loads(request.body)
        Commentaire.objects.create(
            nom=data.get("nom"),
            email=data.get("email"),
            telephone=data.get("telephone"),
            message=data.get("message"),
        )
        return JsonResponse({"status": "success", "message": "Commentaire enregistré avec succès !"})
    return JsonResponse({"status": "error", "message": "Méthode non autorisée"})


# ===================== TEST EMAIL =====================
def test_email(request):
    try:
        send_mail(
            subject='Test HexaQuébec ✉️',
            message='Ceci est un test d’envoi de courriel depuis Django.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['hexaquebec80@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("✅ Email envoyé avec succès !")
    except Exception as e:
        return HttpResponse(f"❌ Erreur : {e}")


import random
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect


import random
def generate_client_code():
    """Génère un code client unique au format HEX-XXXXXX."""
    while True:
        number = random.randint(100000, 999999)  # 6 chiffres
        code = f"HEX-{number}"
        
        if not Client.objects.filter(numero_client=code).exists():
            return code
import string
import secrets

def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))


def client_register(request):
    if request.method == "POST":
        entreprise = request.POST.get("entreprise")
        nom = request.POST.get("nom")
        adresse = request.POST.get("adresse")
        email = request.POST.get("email")

        # Vérifier si email déjà utilisé
        if User.objects.filter(username=email).exists():
            messages.error(request, "Un compte avec ce courriel existe déjà.")
            return redirect('client_register')

        # Créer mot de passe interne (jamais utilisé)
        password = generate_random_password()

        # Créer utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=nom
        )

        # Générer code client
        code_client = generate_client_code()

        # Créer Client
        client = Client.objects.create(
            user=user,
            entreprise=entreprise,
            contact=nom,
            adresse=adresse,
            numero_client=code_client
        )

        # Email au client
        send_mail(
            subject="Votre compte client HexaQuébec",
            message=f"Bonjour {nom},\n\nVotre compte a été créé.\nVotre code client : {code_client}\n\nUtilisez votre email + code client pour vous connecter.\n\nMerci.",
            from_email="hexaquebec80@gmail.com",
            recipient_list=[email],
            fail_silently=False
        )

        messages.success(request, f"Compte créé ! Le code client a été envoyé à {email}.")
        return redirect('client_register')

    return render(request, "register.html")



def client_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("client_code")

        try:
            # Vérifier si le client existe
            client = Client.objects.get(numero_client=code, user__email=email)
            user = client.user
        except Client.DoesNotExist:
            user = None

        if user:
            # Connexion automatique
            login(request, user)
            return redirect("client_profile")
        else:
            messages.error(request, "Email ou code client incorrect.")

    return render(request, "login.html")



@login_required
def client_profile(request):
    client = Client.objects.filter(user=request.user).first()
    if not client:
        return render(request, "session_expiree.html")
    messages_recu = MessageClient.objects.filter(client=client).order_by('-date')

    # Forms (toujours initialisés)
    message_form = MessageClientForm()
    rdv_form = RendezVousForm()
    partenaire_form = PartenaireForm()

    partenaires = Partenaire.objects.all()
    client_est_partenaire = partenaires.filter(id=client.id).exists()

    # ===================== POST =====================
    if request.method == "POST":

        # 📷 PHOTO PROFIL (priorité 1)
        if "photo" in request.FILES:
            client.photo = request.FILES.get("photo")
            client.save()
            messages.success(request, "📸 Photo de profil mise à jour !")
            return redirect("client_profile")

        # 📩 MESSAGE (avec image/fichier)
        elif "send_message" in request.POST:
            message_form = MessageClientForm(request.POST, request.FILES)
            if message_form.is_valid():
                msg = message_form.save(commit=False)
                msg.client = client
                msg.expediteur = request.user
                msg.save()
                messages.success(request, "📩 Votre message a été envoyé.")
                return redirect("client_profile")

        # 📅 RENDEZ-VOUS
        elif "send_rdv" in request.POST:
            rdv_form = RendezVousForm(request.POST)
            if rdv_form.is_valid():
                rdv = rdv_form.save(commit=False)
                rdv.client = client
                rdv.save()
                messages.success(request, "📅 Votre demande de rendez-vous a été envoyée.")
                return redirect("client_profile")

        # 🤝 PARTENARIAT
        elif "send_partenaire" in request.POST:
            partenaire_form = PartenaireForm(request.POST)
            if partenaire_form.is_valid():
                partenaire = partenaire_form.save(commit=False)
                partenaire.client = client
                partenaire.save()
                messages.success(request, "🤝 Votre demande partenaire a été envoyée.")
                return redirect("client_profile")

    # ===================== SERVICES =====================
    services = Service.objects.all()

    # ===================== CONTEXT =====================
    context = {
        "client": client,
        "messages_recu": messages_recu,
        "message_form": message_form,
        "rdv_form": rdv_form,
        "partenaire_form": partenaire_form,
        "partenaires": partenaires,
        "client_est_partenaire": client_est_partenaire,
        "services": services,
    }

    return render(request, "profile.html", context)


@login_required
def messages_client(request):
    client = get_object_or_404(Client, user=request.user)

    # Liste des messages
    messages_list = MessageClient.objects.filter(client=client).order_by('-date')

    # Formulaire
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.client = client
            msg.expediteur = request.user
            msg.save()
            return redirect("messages_client")  # pour éviter double envoi
    else:
        form = MessageForm()

    return render(request, "messages_client.html", {
        "messages_recu": messages_list,
        "client": client,
        "message_form": form
    })




from django.contrib.auth import logout

def client_logout(request):
    """Déconnecte le client et le redirige vers l'accueil"""
    logout(request)  # déconnecte l'utilisateur connecté (ici ton client)
    return redirect('/')  # ou vers la page que tu veux

# ----- FORMULAIRE CLIENT -----
def contact_client(request):
    if request.method == "POST":
        form = ContactClientForm(request.POST)
        if form.is_valid():
            form.save()

            return render(request, "confirmation.html")
    else:
        form = ContactClientForm()

    return render(request, "contact_client.html", {"form": form})


# ----- PAGE ADMIN POUR ENVOYER DES MAILS -----
@login_required
def admin_send_mail(request):
    if not request.user.is_staff:
        return redirect("login")

    form = AdminSendMailForm()

    if request.method == "POST":
        form = AdminSendMailForm(request.POST)
        if form.is_valid():
            send_mail(
                form.cleaned_data["sujet"],
                form.cleaned_data["message"],
                settings.EMAIL_HOST_USER,
                [form.cleaned_data["email"]],
            )
            return render(request, "admin_mail_sent.html")

    return render(request, "admin_send_mail.html", {"form": form})


# ----- LISTE DES MESSAGES REÇUS -----
@login_required
def admin_messages(request):
    if not request.user.is_staff:
        return redirect("login")

    messages = MessageContact.objects.order_by("-date")

    return render(request, "admin_messages.html", {"messages": messages})


from django.contrib.auth import authenticate, login

def login_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("dashboard_admin")  # page après login

        else:
            return render(request, "login_admin.html", {
                "error": "Identifiants incorrects ou accès refusé."
            })

    return render(request, "login_admin.html")


# --- Connexion HexaQuébec ---
def login_hexa(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard_hexa")
    return render(request, "login_hexa.html")


from .models import RapportMensuel


@login_required
def dashboard_hexa(request):

    messages_clients = MessageClient.objects.all().order_by('-date')
    clients = Client.objects.all()
    factures = Facture.objects.all().order_by('date')
    orders = Order.objects.select_related('product').all().order_by('-id')
    paiements = PaiementClient.objects.all().order_by('-date')

    # RAPPORT MENSUEL
    rapports = RapportMensuel.objects.all().order_by('-date')

    total_depenses = sum(
        float(r.montant) for r in rapports
        if r.type == 'depense'
    )

    total_revenus_rapport = sum(
        float(r.montant) for r in rapports
        if r.type == 'revenu'
    )

    benefice = total_revenus_rapport - total_depenses

    # FACTURES CHART
    factures_labels = [f.date.strftime('%b %Y') for f in factures]
    factures_data = [float(f.total_facture()) for f in factures]

    # TES REVENUS FACTURES
    total_revenus = sum(float(f.total_facture()) for f in factures)
    total_non_paye = 0

    return render(request, "dashboard_hexa.html", {
        "messages": messages_clients,
        "clients": clients,
        "factures": factures,
        "orders": orders,

        "clients_paye": paiements,

        "factures_labels": json.dumps(factures_labels),
        "factures_data": json.dumps(factures_data),

        "total_revenus": total_revenus,
        "total_non_paye": total_non_paye,

        # RAPPORT
        "rapports": rapports,
        "total_depenses": total_depenses,
        "total_revenus_rapport": total_revenus_rapport,
        "benefice": benefice,
    })




from django.shortcuts import redirect, get_object_or_404
from .models import RapportMensuel


@login_required
def ajouter_rapport(request):

    if request.method == "POST":

        type_rapport = request.POST.get("type")
        description = request.POST.get("description")
        montant = request.POST.get("montant")

        RapportMensuel.objects.create(
            type=type_rapport,
            description=description,
            montant=montant
        )

    return redirect('dashboard_hexa')


@login_required
def supprimer_rapport(request, id):

    rapport = get_object_or_404(RapportMensuel, id=id)
    rapport.delete()

    return redirect('dashboard_hexa')





@login_required
def rapport_pdf(request):

    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from datetime import datetime

    rapports = RapportMensuel.objects.all().order_by('-date')

    total_revenus_rapport = sum(
        float(r.montant) for r in rapports
        if r.type == 'revenu'
    )

    total_depenses = sum(
        float(r.montant) for r in rapports
        if r.type == 'depense'
    )

    benefice = total_revenus_rapport - total_depenses

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_mensuel_hexaquebec.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # COULEURS
    dark = colors.HexColor("#0b1120")
    card = colors.HexColor("#111827")
    blue = colors.HexColor("#2563eb")
    gold = colors.HexColor("#d4af37")
    green = colors.HexColor("#22c55e")
    red = colors.HexColor("#ef4444")
    light = colors.HexColor("#f8fafc")
    muted = colors.HexColor("#64748b")

    def money(value):
        return f"{value:,.2f} $".replace(",", " ")

    def draw_header():
        # FOND HEADER
        p.setFillColor(dark)
        p.rect(0, height - 120, width, 120, fill=True, stroke=False)

        # TITRE
        p.setFillColor(light)
        p.setFont("Helvetica-Bold", 22)
        p.drawString(40, height - 55, "HexaQuébec")

        p.setFillColor(gold)
        p.setFont("Helvetica-Bold", 15)
        p.drawString(40, height - 80, "Rapport mensuel financier")

        # DATE
        p.setFillColor(colors.white)
        p.setFont("Helvetica", 10)
        today = datetime.now().strftime("%d/%m/%Y")
        p.drawRightString(width - 40, height - 55, f"Généré le : {today}")

        p.setFillColor(muted)
        p.drawRightString(width - 40, height - 75, "Revenus • Dépenses • Bénéfice")

    def draw_footer(page_num):
        p.setFillColor(muted)
        p.setFont("Helvetica", 9)
        p.drawString(40, 25, "HexaQuébec - Rapport confidentiel")
        p.drawRightString(width - 40, 25, f"Page {page_num}")

    def draw_kpi_card(x, y, title, amount, color):
        p.setFillColor(colors.HexColor("#f8fafc"))
        p.roundRect(x, y, 155, 80, 14, fill=True, stroke=False)

        p.setFillColor(color)
        p.roundRect(x + 12, y + 50, 32, 18, 8, fill=True, stroke=False)

        p.setFillColor(muted)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x + 15, y + 35, title)

        p.setFillColor(dark)
        p.setFont("Helvetica-Bold", 17)
        p.drawString(x + 15, y + 15, money(amount))

    page_num = 1

    draw_header()
    draw_footer(page_num)

    # CARTES KPI
    y = height - 220

    draw_kpi_card(40, y, "REVENUS", total_revenus_rapport, green)
    draw_kpi_card(220, y, "DÉPENSES", total_depenses, red)

    benefice_color = green if benefice >= 0 else red
    draw_kpi_card(400, y, "BÉNÉFICE NET", benefice, benefice_color)

    # TITRE TABLE
    y -= 60

    p.setFillColor(dark)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Détails des transactions")

    y -= 30

    # HEADER TABLE
    p.setFillColor(blue)
    p.roundRect(40, y - 8, width - 80, 30, 8, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)

    p.drawString(55, y, "Date")
    p.drawString(135, y, "Type")
    p.drawString(230, y, "Description")
    p.drawRightString(width - 55, y, "Montant")

    y -= 35

    p.setFont("Helvetica", 9)

    if not rapports:
        p.setFillColor(muted)
        p.drawString(55, y, "Aucune donnée disponible.")
    else:
        for index, r in enumerate(rapports):

            if y < 70:
                p.showPage()
                page_num += 1
                draw_header()
                draw_footer(page_num)

                y = height - 160

                p.setFillColor(blue)
                p.roundRect(40, y - 8, width - 80, 30, 8, fill=True, stroke=False)

                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 10)

                p.drawString(55, y, "Date")
                p.drawString(135, y, "Type")
                p.drawString(230, y, "Description")
                p.drawRightString(width - 55, y, "Montant")

                y -= 35
                p.setFont("Helvetica", 9)

            # LIGNE ALTERNÉE
            if index % 2 == 0:
                p.setFillColor(colors.HexColor("#f1f5f9"))
                p.roundRect(40, y - 8, width - 80, 26, 6, fill=True, stroke=False)

            # DATE
            p.setFillColor(dark)
            p.drawString(55, y, str(r.date))

            # BADGE TYPE
            if r.type == "revenu":
                type_color = green
                type_text = "Revenu"
            else:
                type_color = red
                type_text = "Dépense"

            p.setFillColor(type_color)
            p.roundRect(130, y - 5, 70, 17, 7, fill=True, stroke=False)

            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 8)
            p.drawCentredString(165, y, type_text)

            # DESCRIPTION
            p.setFillColor(dark)
            p.setFont("Helvetica", 9)

            description = r.description
            if len(description) > 45:
                description = description[:45] + "..."

            p.drawString(230, y, description)

            # MONTANT
            p.setFont("Helvetica-Bold", 9)
            p.setFillColor(type_color)
            p.drawRightString(width - 55, y, money(float(r.montant)))

            y -= 28

    # RÉSUMÉ FINAL
    if y < 130:
        p.showPage()
        page_num += 1
        draw_header()
        draw_footer(page_num)
        y = height - 170

    y -= 30

    p.setFillColor(dark)
    p.roundRect(40, y - 70, width - 80, 80, 14, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(60, y - 10, "Résumé financier")

    p.setFont("Helvetica", 11)
    p.drawString(60, y - 35, f"Total revenus : {money(total_revenus_rapport)}")
    p.drawString(240, y - 35, f"Total dépenses : {money(total_depenses)}")

    p.setFillColor(gold)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(420, y - 35, f"Bénéfice : {money(benefice)}")

    p.save()

    return response




from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import MessageClient


def repondre_message(request, message_id):

    message_obj = get_object_or_404(MessageClient, id=message_id)

    if request.method == "POST":

        reponse = request.POST.get("reponse", "").strip()

        if not reponse:
            messages.error(request, "Veuillez écrire une réponse.")
            return redirect("repondre_message", message_id=message_id)

        message_obj.reponse = reponse
        message_obj.date_reponse = timezone.now()
        message_obj.save()

        client = message_obj.client.user

        subject = "📩 Réponse à votre message - Hexa Québec"

        email_body = f"""
Bonjour {client.username},

Vous avez reçu une nouvelle réponse de HexaQuébec.

━━━━━━━━━━━━━━━━━━━━

📩 Votre message :
{message_obj.message}

━━━━━━━━━━━━━━━━━━━━

💬 Notre réponse :
{reponse}

━━━━━━━━━━━━━━━━━━━━

🔗 https://hexaquebec.com

━━━━━━━━━━━━━━━━━━━━

Équipe HexaQuébec
Support Client
"""

        if client.email:
            send_mail(
                subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [client.email],
                fail_silently=False,
            )

        messages.success(request, "Réponse envoyée avec succès.")

        return redirect("dashboard_hexa")

    return render(request, "repondre_message.html", {
        "message": message_obj
    })

@login_required
def envoyer_message(request):
    message_envoye = False

    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES)  # Important : request.FILES pour fichiers
        if form.is_valid():
            message_obj = form.save(commit=False)
            message_obj.expediteur = request.user
            message_obj.save()

            # Email HTML
            context = {
                "user": request.user,
                "message": message_obj,
                "logo_url": request.build_absolute_uri('/static/images/logoHexa.png')
            }
            html_content = render_to_string('email_template.html', context)

            email = EmailMessage(
                subject=f"Nouveau message de {request.user.username}",
                body=html_content,
                from_email="hexaquebec80@gmail.com",
                to=[message_obj.destinataire_email]
            )
            email.content_subtype = "html"

            # Gestion du fichier si présent
            if message_obj.fichier:
                message_obj.fichier.open()  # ouvre le fichier
                mime_type, _ = mimetypes.guess_type(message_obj.fichier.name)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                email.attach(message_obj.fichier.name, message_obj.fichier.read(), mime_type)

            email.send()
            message_envoye = True

    else:
        form = MessageForm()

    return render(
        request,
        "envoyer_message.html",
        {"form": form, "message_envoye": message_envoye}
    )


from .forms import OrderForm  # si tu utilises un form; sinon adapte
from io import BytesIO
import base64
import qrcode


# bibliothèques pour barcode / qrcode / pdf
import barcode
from barcode.writer import ImageWriter
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def _generate_code128_base64(text):
    """Retourne une image PNG (base64) du code-barres code128 pour `text`."""
    CODE128 = barcode.get_barcode_class('code128')
    rv = BytesIO()
    barcode_img = CODE128(str(text), writer=ImageWriter())
    barcode_img.write(rv, {'format': 'PNG'})
    return base64.b64encode(rv.getvalue()).decode('utf-8')


def _generate_qrcode_base64(text):
    """Retourne une image PNG (base64) du QR Code pour `text`."""
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(str(text))
    qr.make(fit=True)
    img = qr.make_image()
    rv = BytesIO()
    img.save(rv, format='PNG')
    return base64.b64encode(rv.getvalue()).decode('utf-8')


# ---------- Vue création / affichage commande ----------

def order_view(request, produit_id):

    product = get_object_or_404(Product, id=produit_id)

    if request.method == 'POST':

        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        courriel = request.POST.get('courriel')

        # Vérifier champs obligatoires
        if not all([nom, prenom, adresse, telephone, courriel]):
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'order_page.html', {'product': product})

        # Vérifier email
        try:
            validate_email(courriel)
        except ValidationError:
            messages.error(request, "Email invalide.")
            return render(request, 'order_page.html', {'product': product})

        order = Order.objects.create(
            product=product,
            nom=nom,
            prenom=prenom,
            adresse=adresse,
            telephone=telephone,
            courriel=courriel
        )

        return redirect('checkout', product_id=order.product.id)

    return render(request, 'order_page.html', {'product': product})



from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    price = float(product.price)
    tps = price * 0.05
    tvq = price * 0.09975
    total = round(price + tps + tvq, 2)

    amount_cents = int(total * 100)

    # ✅ créer la commande
    order = Order.objects.create(
        product=product,
        price=price,
        tps=tps,
        tvq=tvq,
        total=total,
        paid=False
    )

    # ✅ Stripe avec metadata
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="cad",
        description=f"Achat de {product.title}",
        metadata={
            "order_id": order.id
        }
    )

    return render(request, "checkout.html", {
        "product": product,
        "client_secret": intent.client_secret,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        "total": total,
        "order_id": order.id  # 🔥 important
    })

def payment_success(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    prix = float(order.product.price)

    tps = round(prix * 0.05, 2)
    tvq = round(prix * 0.09975, 2)
    total = round(prix + tps + tvq, 2)

    # Générer tracking simple
    order.tracking_number = f"HEX-{order.id}{order.code[:4]}"
    order.save()

    # Email client
    send_mail(

        "Commande confirmée - HexaQuébec",

        f"""
Merci pour votre commande !

Produit : {order.product.title}

Total payé : {total} CAD

Numéro de commande : {order.code}

Tracking livraison : {order.tracking_number}

Merci de votre confiance.
HexaQuébec
""",

        settings.EMAIL_HOST_USER,
        [order.courriel],
        fail_silently=True
    )

    return redirect('order_receipt', order_id=order.id)

def order_receipt(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    prix = float(order.product.price)

    TPS = round(prix * 0.05, 2)
    TVQ = round(prix * 0.09975, 2)

    total = round(prix + TPS + TVQ, 2)

    barcode_base64 = _generate_code128_base64(order.code)
    qrcode_base64 = _generate_qrcode_base64(
        f"COMMANDE#{order.code} - {order.product.title}"
    )

    return render(request, 'order_receipt.html', {

        'order': order,
        'TPS': TPS,
        'TVQ': TVQ,
        'total': total,
        'barcode_base64': barcode_base64,
        'qrcode_base64': qrcode_base64,
    })

def download_order_pdf(request, order_id):

    order = Order.objects.get(id=order_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{order.id}.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("FACTURE - HexaQuebec", styles['Title']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"Commande #: {order.id}", styles['Normal']))
    elements.append(Paragraph(f"Client: {order.client.email}", styles['Normal']))
    elements.append(Paragraph(f"Produit: {order.product.title}", styles['Normal']))
    elements.append(Paragraph(f"Prix: {order.total}$ CAD", styles['Normal']))

    elements.append(Spacer(1,20))

    data = [
        ["Produit", "Prix"],
        [order.product.title, f"{order.total}$"]
    ]

    table = Table(data)
    elements.append(table)

    elements.append(Spacer(1,30))

    elements.append(Paragraph(
        "Paiement validé. Votre commande sera envoyée dans quelques jours. Merci pour votre confiance.",
        styles['Normal']
    ))

    pdf.build(elements)

    return response
# ---------- Vue simple pour order_product ----------

def order_product(request, product_id):
    produit = Product.objects.get(id=product_id)
    return render(request, "order_page.html", {"product": produit})


from django.http import JsonResponse

def like_produit(request, pk):
    produit = produit.objects.get(id=pk)
    produit.likes += 1
    produit.save()
    return JsonResponse({"likes": produit.likes})



def developp_detail(request):
    return render(request, 'developp_detail.html')

def dev_page(request):
    # Tu peux ajouter des données dans context si nécessaire
    context = {}
    return render(request, 'dev_page.html', context)
@csrf_exempt  # uniquement si pas de compte utilisateur
def like_toggle(request, product_id):
    if request.method == "POST":
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Produit introuvable'}, status=404)

        # On stocke les likes pour les non-connectés via session
        session_likes = request.session.get('liked_products', [])

        # Convertir product_id en int pour comparaison
        product_id_int = int(product_id)

        if product_id_int not in session_likes:
            # incrémente le compteur
            product.likes += 1
            product.save()

            # enregistre le like dans la session
            session_likes.append(product_id_int)
            request.session['liked_products'] = session_likes

            return JsonResponse({'count': product.likes})
        else:
            return JsonResponse({'count': product.likes, 'message': 'Vous avez déjà liké !'})

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def service_web_mobile(request):
    return render(request, 'service_web_mobile.html')


def service_marketing(request):
    return render(request, "service_marketing.html")


def service_maintenance(request):
    return render(request, "service_maintenance.html")


def service_ai(request):
    return render(request, "service_ai.html")




from .models import Facture

def generer_numero():

    last = Facture.objects.last()

    if not last:
        return "HEXA-0001"

    number = int(last.numero.split("-")[1]) + 1

    return f"HEXA-{number:04d}"

from django.shortcuts import render, redirect
from .models import Facture, LigneFacture
from decimal import Decimal


def creer_facture(request):

    if request.method == "POST":

        vendeur = request.POST.get("vendeur")
        acheteur = request.POST.get("acheteur")

        # 👉 adresse client (AJOUT IMPORTANT)
        adresse = request.POST.get("adresse_client")
        ville = request.POST.get("ville_client")
        code_postal = request.POST.get("code_postal_client")
        pays = request.POST.get("pays_client")

        date = request.POST.get("date")
        signature = request.POST.get("signature")

        # 👉 création facture (numéro automatique dans model.save)
        facture = Facture.objects.create(
            vendeur_nom=vendeur,
            acheteur_nom=acheteur,
            adresse_client=adresse,
            ville_client=ville,
            code_postal_client=code_postal,
            pays_client=pays,
            date=date,
            signature_vendeur=signature
        )

        # 👉 produits multiples
        produits = request.POST.getlist("produit[]")
        quantites = request.POST.getlist("quantite[]")
        prix = request.POST.getlist("prix_unitaire[]")

        for p, q, pr in zip(produits, quantites, prix):

            LigneFacture.objects.create(
                facture=facture,
                produit=p,
                quantite=int(q),
                prix_unitaire=Decimal(pr)
            )

        return redirect("facture_detail", id=facture.id)

    return render(request, "facture_form.html")

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import base64
from io import BytesIO


def fact_pdf(request, facture_id):

    facture = get_object_or_404(Facture, id=facture_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="facture_{facture.numero}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ======================
    # HEADER
    # ======================
    p.setFillColor(HexColor("#2c3e50"))
    p.setFont("Helvetica-Bold", 24)
    p.drawString(40, height - 50, "HexaQuébec")

    p.setFont("Helvetica-Bold", 18)
    p.drawRightString(width - 40, height - 50, f"FACTURE #{facture.numero}")

    p.line(40, height - 60, width - 40, height - 60)

    # ======================
    # ADRESSES
    # ======================
    y = height - 100

    # ENTREPRISE
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, y, "HexaQuébec")

    p.setFont("Helvetica", 10)
    p.drawString(40, y - 15, "2186 Rue Roussel")
    p.drawString(40, y - 30, "Chicoutimi, QC G7G 1W6")
    p.drawString(40, y - 45, "Canada")
    p.drawString(40, y - 60, "hexaquebec80@gmail.com")

    # CLIENT
    p.setFont("Helvetica-Bold", 11)
    p.drawString(width / 2, y, "Facturé à :")

    p.setFont("Helvetica", 10)
    p.drawString(width / 2, y - 15, facture.acheteur_nom)
    p.drawString(width / 2, y - 30, facture.adresse_client)
    p.drawString(width / 2, y - 45,
                 f"{facture.ville_client} - {facture.code_postal_client}")
    p.drawString(width / 2, y - 60, facture.pays_client)

    # VENDEUR + DATE
    p.setFont("Helvetica-Bold", 11)
    p.drawString(width / 2, y - 85, "Vendeur :")

    p.setFont("Helvetica", 10)
    p.drawString(width / 2, y - 100, facture.vendeur_nom)
    p.drawString(width / 2, y - 115, f"Date : {facture.date}")

    # ======================
    # TABLE HEADER
    # ======================
    table_y = y - 150

    p.setFillColor(HexColor("#2c3e50"))
    p.rect(40, table_y, width - 80, 25, fill=1)

    p.setFillColor("white")
    p.setFont("Helvetica-Bold", 11)

    p.drawString(50, table_y + 7, "Produit")
    p.drawString(300, table_y + 7, "Qté")
    p.drawString(380, table_y + 7, "Prix")
    p.drawString(460, table_y + 7, "Total")

    # ======================
    # LIGNES PRODUITS
    # ======================
    p.setFillColor("black")
    p.setFont("Helvetica", 11)

    y = table_y - 25
    subtotal = Decimal("0.00")

    for ligne in facture.lignes.all():

        total_ligne = Decimal(str(ligne.total()))
        subtotal += total_ligne

        p.drawString(50, y, str(ligne.produit))
        p.drawString(300, y, str(ligne.quantite))
        p.drawString(380, y, f"{ligne.prix_unitaire} $")
        p.drawString(460, y, f"{total_ligne:.2f} $")

        y -= 20

    # ======================
    # TAXES (CORRIGÉ)
    # ======================
    tps = subtotal * Decimal("0.05")
    tvq = subtotal * Decimal("0.09975")
    total = subtotal + tps + tvq

    total_y = y - 40

    p.setFont("Helvetica", 11)

    p.drawRightString(width - 150, total_y, "Sous-total :")
    p.drawRightString(width - 40, total_y, f"{subtotal:.2f} $")

    p.drawRightString(width - 150, total_y - 18, "TPS (5%) :")
    p.drawRightString(width - 40, total_y - 18, f"{tps:.2f} $")

    p.drawRightString(width - 150, total_y - 36, "TVQ (9.975%) :")
    p.drawRightString(width - 40, total_y - 36, f"{tvq:.2f} $")

    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width - 150, total_y - 70, "TOTAL :")
    p.drawRightString(width - 40, total_y - 70, f"{total:.2f} $")

    # ======================
    # SIGNATURE
    # ======================
    p.setFont("Helvetica", 11)
    p.drawString(40, total_y - 90, "Signature :")

    signature = facture.signature_vendeur

    if signature and "base64" in signature:
        _, imgstr = signature.split(";base64,")
        img_data = base64.b64decode(imgstr)
        image = ImageReader(BytesIO(img_data))

        p.drawImage(image, 120, total_y - 110,
                    width=150, height=50, mask="auto")

    # ======================
    # FOOTER
    # ======================
    p.line(40, 120, width - 40, 120)

    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, 90, "FACTURE OFFICIELLE - HexaQuébec")

    p.setFont("Helvetica", 9)
    p.drawString(40, 75, "Développement Web | Mobile | IA | Design | Infographie")
    p.drawString(40, 60, "Vente de services informatiques | Maintenance ordinateur")
    p.drawString(40, 45, "Canada - Québec")

    p.showPage()
    p.save()

    return response



from django.shortcuts import render, get_object_or_404
from decimal import Decimal

def facture_detail(request, id):
    facture = get_object_or_404(Facture, id=id)
    lignes = facture.lignes.all()

    subtotal = Decimal(str(facture.total_facture()))

    tps = subtotal * Decimal("0.05")
    tvq = subtotal * Decimal("0.09975")
    total = subtotal + tps + tvq

    context = {
        "facture": facture,
        "lignes": lignes,
        "subtotal": subtotal,
        "tps": tps,
        "tvq": tvq,
        "total": total
    }

    return render(request, "facture_detail.html", context)


def facture_list(request):
    factures = Facture.objects.all().order_by('-created_at')

    return render(request, "facture_list.html", {
        "factures": factures
    })



from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal

def facture_edit(request, id):

    facture = get_object_or_404(Facture, id=id)

    if request.method == "POST":

        # ======================
        # INFO FACTURE
        # ======================
        facture.vendeur_nom = request.POST.get("vendeur_nom")
        facture.acheteur_nom = request.POST.get("acheteur_nom")
        facture.date = request.POST.get("date")
        facture.signature_vendeur = request.POST.get("signature_vendeur")

        facture.adresse_client = request.POST.get("adresse_client")
        facture.ville_client = request.POST.get("ville_client")
        facture.code_postal_client = request.POST.get("code_postal_client")
        facture.pays_client = request.POST.get("pays_client")

        facture.save()

        # ======================
        # PRODUITS (LIGNES)
        # ======================
        for ligne in facture.lignes.all():

            produit = request.POST.get(f"produit_{ligne.id}")
            quantite = request.POST.get(f"quantite_{ligne.id}")
            prix = request.POST.get(f"prix_{ligne.id}")

            if produit and quantite and prix:
                ligne.produit = produit
                ligne.quantite = int(quantite)
                ligne.prix_unitaire = Decimal(prix)
                ligne.save()

        return redirect("facture_detail", id=facture.id)

    return render(request, "facture_edit.html", {
        "facture": facture,
        "lignes": facture.lignes.all()
    })



from django.contrib import messages
from django.shortcuts import redirect

@login_required
def facture_delete(request, facture_id):

    facture = get_object_or_404(Facture, id=facture_id)

    if request.method == "POST":
        facture.delete()
        messages.success(request, "Facture supprimée avec succès !")

    return redirect('facture_list')

def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1

    item.save()

    return redirect("view_cart")


def view_cart(request):

    cart = Cart.objects.get(user=request.user)

    total = 0

    for item in cart.items.all():
        total += item.product.price * item.quantity

    return render(request, "cart.html", {
        "cart": cart,
        "total": total
    })


def remove_from_cart(request, item_id):

    item = CartItem.objects.get(id=item_id)

    item.delete()

    return redirect("view_cart")


from django.core.mail import send_mail






def merci(request):
    return render(request, "merci.html")


from xhtml2pdf import pisa



def facture_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    template_path = 'facture_template.html'  # ton template PDF
    context = {'order': order}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{order.code}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF <pre>' + html + '</pre>')
    return response




from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def envoyer_email_commande(order):

    subject = "Confirmation de paiement - HexaQuébec"
    from_email = "HexaQuébec <tonemail@gmail.com>"
    to = [order.courriel]

    html_content = f"""
    <div style="font-family:Arial; background:#f4f6f8; padding:30px;">
        <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:10px;">
            
            <h2 style="color:#e67e22;">Paiement confirmé ✅</h2>

            <p>Bonjour <strong>{order.prenom}</strong>,</p>

            <p>Votre paiement a été validé avec succès.</p>

            <p>📦 Votre commande sera envoyée dans quelques jours.</p>

            <p style="background:#f8f9fa; padding:10px; border-radius:6px;">
                🛡 <strong>Garantie :</strong> Votre produit est garanti 1 an par HexaQuébec.
            </p>

            <hr>

            <h3>Détails de votre commande</h3>
            <p><strong>Produit :</strong> {order.product.title}</p>
            <p><strong>Montant :</strong> {order.total} $</p>

            <hr>

            <p style="font-size:12px; color:#888;">
                Merci pour votre confiance 🙏<br>
                HexaQuébec - Solutions informatiques<br>
                www.hexaquebec.com
            </p>

        </div>
    </div>
    """

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")

    msg.send()





def generer_facture_pdf(order):
    html = render_to_string('facture.html', {'order': order})
    
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return None

    return result.getvalue()


def envoyer_email_commande(order):

    subject = "Facture et confirmation - HexaQuébec"
    from_email = "HexaQuébec <tonemail@gmail.com>"
    to = [order.courriel]

    html_content = f"""
    <h2>Paiement confirmé ✅</h2>
    <p>Bonjour {order.prenom},</p>
    <p>Votre commande sera envoyée dans quelques jours.</p>
    <p><strong>Garantie 1 an par HexaQuébec</strong></p>
    """

    pdf = generer_facture_pdf(order)

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")

    # joindre PDF
    msg.attach(f"facture_{order.code}.pdf", pdf, "application/pdf")

    msg.send()




def paiement_reussi(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.paid:
        order.paid = True
        order.save()

        # 🔥 ENVOI EMAIL ICI
        envoyer_email_commande(order)

    return redirect('merci')


import json
from django.http import JsonResponse

def sauvegarder_client(request):
    if request.method == "POST":
        data = json.loads(request.body)

        order = Order.objects.get(id=data['order_id'])

        order.nom = data['nom']
        order.prenom = data['prenom']
        order.courriel = data['email']
        order.adresse = data['adresse']
        order.telephone = data['telephone']

        order.save()

        return JsonResponse({"status": "ok"})
    


from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Panier, PanierItem

def panier_view(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    panier, _ = Panier.objects.get_or_create(session_id=session_id)

    return render(request, 'panier.html', {'panier': panier})


def ajouter_au_panier(request, produit_id):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    panier, _ = Panier.objects.get_or_create(session_id=session_id)
    produit = get_object_or_404(Product, id=produit_id)

    item, created = PanierItem.objects.get_or_create(panier=panier, produit=produit)
    if not created:
        item.quantite += 1
        item.save()

    return redirect('panier')


def supprimer_du_panier(request, item_id):
    item = get_object_or_404(PanierItem, id=item_id)
    item.delete()
    return redirect('panier')



import random
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Stagiaire


## ================= DEMANDE DE STAGE =================
def demande_stage(request):
    if request.method == "POST":

        # 🔹 Récupération données
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        niveau = request.POST.get("niveau")
        specialite = request.POST.get("specialite")
        programme = request.POST.get("programme_info")
        date_naissance = request.POST.get("date_naissance")
        lieu_naissance = request.POST.get("lieu_naissance")
        commentaire = request.POST.get("commentaire")
        cv = request.FILES.get("cv")
        lettre_convention = request.FILES.get("lettre_convention")
        date_debut_str = request.POST.get("date_debut")

        # 🔴 Vérification champs obligatoires
        if not nom or not email or not cv:
            messages.error(request, "❌ Veuillez remplir tous les champs obligatoires.")
            return render(request, "demande_stage.html")

        # 🔴 Vérifier email déjà utilisé
        if Stagiaire.objects.filter(email=email).exists():
            messages.error(
                request,
                "❌ Cet email est déjà enregistré ou une demande est en cours."
            )
            return render(request, "demande_stage.html")

        # 🔴 Vérification date début
        if not date_debut_str:
            messages.error(request, "❌ Veuillez sélectionner la date de début du stage.")
            return render(request, "demande_stage.html")

        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "❌ Format de date invalide.")
            return render(request, "demande_stage.html")

        # 🔢 Code interne
        code = str(random.randint(1000, 9999))

        try:
            # ✅ Création stagiaire
            Stagiaire.objects.create(
                nom=nom,
                email=email,
                niveau=niveau,
                specialite=specialite,
                programme=programme,
                date_naissance=date_naissance,
                lieu_naissance=lieu_naissance,
                date_debut=date_debut,
                commentaire=commentaire,
                cv=cv,
                lettre_convention=lettre_convention,
                code=code
            )

            # ================= EMAIL =================
            subject = "Demande de stage reçue - HexaQuébec"

            html_message = render_to_string("email.html", {
                "nom": nom,
            })

            plain_message = strip_tags(html_message)

            send_mail(
                subject,
                plain_message,
                settings.EMAIL_HOST_USER,
                [email],
                html_message=html_message,
                fail_silently=False,
            )

            # ✅ Message succès
            messages.success(
                request,
                "✅ Votre demande a été envoyée avec succès. Vérifiez votre email."
            )

            return redirect("home")

        except Exception as e:
            messages.error(
                request,
                "❌ Une erreur est survenue lors de l'envoi. Réessayez."
            )
            return render(request, "demande_stage.html")

    return render(request, "demande_stage.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Stagiairelogin, ProfilStagiaire
from .models import Stagiairelogin, ProfilStagiaire


# ================= LOGIN =================
def login_stagiaire(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")

        try:
            login = Stagiairelogin.objects.get(email=email)

            # ❌ REFUS
            if login.refuse:
                messages.error(request, "Votre demande a été refusée.")
                return redirect("login_stagiaire")

            # ⏳ EN ATTENTE
            if not login.accepte:
                messages.error(request, "Votre demande est en cours de validation.")
                return redirect("login_stagiaire")

            # 🔐 CODE
            if login.code != code:
                messages.error(request, "Code incorrect.")
                return redirect("login_stagiaire")

            # ✅ SESSION
            request.session["stagiaire_id"] = login.id

            return redirect("dashboard_stagiaire")

        except Stagiairelogin.DoesNotExist:
            messages.error(request, "Email introuvable.")
            return redirect("login_stagiaire")

    return render(request, "login_stagiaire.html")


# ================= DASHBOARD =================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from .models import (
    Stagiairelogin,
    ProfilStagiaire,
    PresenceStagiaire,
)

from .forms import ProfilStagiaireForm
from .models import MessageStagiaire
from datetime import datetime
from .models import DocumentStagiaire

def dashboard_stagiaire(request):

    # ================= SESSION =================

    stagiaire_id = request.session.get("stagiaire_id")

    if not stagiaire_id:
        return redirect("login_stagiaire")

    # ================= USER =================

    login = Stagiairelogin.objects.get(id=stagiaire_id)

    stagiaire = login.stagiaire

    profil, created = ProfilStagiaire.objects.get_or_create(
        stagiaire=stagiaire
    )

    # ================= PRESENCE JOUR =================

    today = timezone.now().date()

    presence, created = PresenceStagiaire.objects.get_or_create(
        profil=profil,
        date=today
    )

    # ================= HISTORIQUE =================

    historique_presences = PresenceStagiaire.objects.filter(
        profil=profil
    ).order_by("-date")

    # ================= POST =================

    if request.method == "POST":

        # =====================================================
        # 📅 RDV
        # =====================================================

        if "send_rdv" in request.POST:

            date = request.POST.get("date")
            heure = request.POST.get("heure")

            if date and heure:

                datetime_str = f"{date} {heure}"

                profil.date_rdv = datetime.strptime(
                    datetime_str,
                    "%Y-%m-%d %H:%M"
                )

                profil.statut_rdv = "en_attente"

                profil.save()

                messages.success(
                    request,
                    "📅 Demande de rendez-vous envoyée"
                )

            else:

                messages.error(
                    request,
                    "Veuillez choisir date et heure"
                )

            return redirect("dashboard_stagiaire")


        # =====================================================
        # 💬 MESSAGE
        # =====================================================

        if "send_message" in request.POST:

            msg = request.POST.get("message_stagiaire")

            if msg:

                MessageStagiaire.objects.create(
                    profil=profil,
                    auteur="stagiaire",
                    message=msg
                )

                messages.success(
                    request,
                    "💬 Message envoyé à l'administration"
                )

            else:

                messages.error(
                    request,
                    "Veuillez écrire un message"
                )

            return redirect("dashboard_stagiaire")


        # =====================================================
        # 🟢 POINTAGE ENTRÉE
        # =====================================================

        if "pointer_entree" in request.POST:

            if not presence.pointage_entree:

                presence.pointage_entree = timezone.now().time()

                presence.save()

                messages.success(
                    request,
                    "🟢 Entrée enregistrée"
                )

            else:

                messages.warning(
                    request,
                    "Entrée déjà enregistrée"
                )

            return redirect("dashboard_stagiaire")

        # =====================================================
        # 🍽️ PAUSE REPAS
        # =====================================================

        if "pause_repas" in request.POST:

            repas = request.POST.get("repas")

            presence.pause_repas = repas

            presence.save()

            messages.success(
                request,
                "🍽️ Pause repas enregistrée"
            )

            return redirect("dashboard_stagiaire")

        # =====================================================
        # 🔴 POINTAGE SORTIE
        # =====================================================

        if "pointer_sortie" in request.POST:

            if not presence.pointage_sortie:

                presence.pointage_sortie = timezone.now().time()

                presence.save()

                messages.success(
                    request,
                    "🔴 Sortie enregistrée"
                )

            else:

                messages.warning(
                    request,
                    "Sortie déjà enregistrée"
                )

            return redirect("dashboard_stagiaire")

        # =====================================================
        # 🚨 ABSENCE
        # =====================================================

        if "signaler_absence" in request.POST:

            raison = request.POST.get("raison_absence")

            presence.absent = True

            presence.raison_absence = raison

            presence.save()

            messages.warning(
                request,
                "🚨 Absence signalée"
            )

            return redirect("dashboard_stagiaire")
        

        # =====================================================
        # 📄 DOCUMENT
        # =====================================================

        if "upload_document" in request.POST:

            titre = request.POST.get("titre")
            fichier = request.FILES.get("fichier")

            if titre and fichier:

                DocumentStagiaire.objects.create(
                    profil=profil,
                    titre=titre,
                    fichier=fichier
                )

                messages.success(
                    request,
                    "📄 Document envoyé avec succès"
                )

            else:

                messages.error(
                    request,
                    "Veuillez sélectionner un fichier"
                )

            return redirect("dashboard_stagiaire")

    
        # =====================================================
        # 📷 PHOTO
        # =====================================================

        form = ProfilStagiaireForm(
            request.POST,
            request.FILES,
            instance=profil
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "📷 Photo mise à jour avec succès"
            )

            return redirect("dashboard_stagiaire")

        else:

            messages.error(
                request,
                "Erreur lors de l'envoi de la photo"
            )


    else:

        form = ProfilStagiaireForm(instance=profil)

    # ================= DOCUMENTS =================

    documents = profil.documents.all().order_by("-date_ajout")

    # ================= RENDER =================

    return render(request, "dashboard_stagiaire.html", {

        "stagiaire": stagiaire,

        "profil": profil,

        "form": form,

        # PRESENCE JOUR
        "presence": presence,

        # HISTORIQUE
        "historique_presences": historique_presences,

        # DOCUMENTS
        "documents": documents,
    })





# ================= LOGOUT =================
def logout_stagiaire(request):
    request.session.flush()
    return redirect("login_stagiaire")



def space(request):
    return render(request, "space.html")



from django.contrib import messages
from .models import Stagiairelogin

def accepter_stagiaire(request, id):
    stagiaire = get_object_or_404(Stagiairelogin, id=id)

    stagiaire.accepte = True
    stagiaire.generer_code()

    messages.success(request, f"Stagiaire accepté. Code : {stagiaire.code}")

    return redirect("liste_stagiaires")




def envoyer_email_acceptation(self):
    subject = "Demande de stage acceptée - HexaQuébec"
    message = f"""
Bonjour {self.email},

Votre demande de stage a été acceptée par HexaQuébec.

Voici vos informations pour accéder à votre compte stagiaire :
Email : {self.email}
Code d'accès : {self.code}

Nous vous enverrons bientôt votre programme et le responsable de votre stage.

Merci !
"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email], fail_silently=False)
    except Exception as e:
        print(f"Erreur email acceptation: {e}")

def envoyer_email_refus(self):
    subject = "Demande de stage refusée - HexaQuébec"
    message = f"""
Bonjour {self.email},

Nous sommes désolés de vous informer que votre demande de stage a été refusée.

Merci pour votre intérêt et à bientôt.
"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email], fail_silently=False)
    except Exception as e:
        print(f"Erreur email refus: {e}")



    
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
import os
def generer_attestation(self):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        name="Title",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0b132b"),
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        name="Subtitle",
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1c2541"),
        spaceAfter=15
    )
    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0b132b"),
        spaceAfter=10
    )

    elements = []

    # Logo
    logo_path = os.path.join('static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=120, height=60))
        elements.append(Spacer(1, 20))

    # Titre principal
    elements.append(Paragraph("ATTESTATION DE STAGE", title_style))
    elements.append(Paragraph("Conforme aux normes professionnelles du Québec", subtitle_style))
    elements.append(Spacer(1, 20))

    # Contenu
    date_debut = getattr(self.stagiaire, 'date_debut', 'Non défini')
    date_fin = getattr(self.stagiaire, 'date_fin', 'Non défini')
    specialite = getattr(self.stagiaire, 'specialite', 'Non défini')

    texte = f"""
    <b>Nom du stagiaire :</b> {self.stagiaire.nom}<br/>
    <b>Spécialité :</b> {specialite}<br/>
    <b>Période :</b> du {date_debut} au {date_fin}<br/>
    <b>Code stagiaire :</b> {self.code_stagiaire}
    """
    elements.append(Paragraph(texte, normal_style))
    elements.append(Spacer(1, 30))

    # Signature
    elements.append(Paragraph("Fait à Québec, le " + str(self.date_debut), normal_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>HexaQuébec</b>", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("__________________________", normal_style))
    elements.append(Paragraph("Signature autorisée", normal_style))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return ContentFile(pdf, name=f"attestation_{self.code_stagiaire}.pdf")



import io
import qrcode
import os

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle, Spacer
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


@login_required
def carte_affaire_pdf(request):

    client = getattr(request.user, "client", None)
    if not client:
        return HttpResponse("Client introuvable", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carte_client.pdf"'

    width, height = (85 * mm, 55 * mm)

    doc = SimpleDocTemplate(
        response,
        pagesize=(width, height),
        leftMargin=3,
        rightMargin=3,
        topMargin=3,
        bottomMargin=3
    )

    styles = getSampleStyleSheet()
    gold = colors.HexColor("#C6A87D")

    # ======================
    # 🔐 SECURE TEXT
    # ======================
    def safe(text, max_len=30):
        return str(text)[:max_len] if text else ""

    # ======================
    # 🎨 STYLES (réduits)
    # ======================
    header_style = ParagraphStyle(
        "header",
        parent=styles["Normal"],
        fontSize=7,  # 🔥 réduit
        textColor=gold,
        alignment=1,
        spaceAfter=2
    )

    title_style = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=1,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        "subtitle",
        parent=styles["Normal"],
        fontSize=6,
        textColor=gold,
        alignment=1,
        spaceAfter=2
    )

    info_style = ParagraphStyle(
        "info",
        parent=styles["Normal"],
        fontSize=6,
        textColor=colors.HexColor("#E5E7EB"),
        alignment=1,
        leading=7
    )

    id_style = ParagraphStyle(
        "id",
        parent=styles["Normal"],
        fontSize=5.5,
        textColor=gold,
        alignment=1,
        spaceBefore=2
    )

    # ======================
    # 🖼️ LOGO (petit)
    # ======================
    logo_path = os.path.join(settings.STATIC_ROOT, "images/logoHexa.png")

    if os.path.exists(logo_path):
        logo = Image(logo_path, 20*mm, 20*mm)
    else:
        logo = Spacer(1, 12*mm)

    # ======================
    # 🔳 QR CODE (petit)
    # ======================
    qr_data = f"{client.entreprise} | {client.contact}"
    qr = qrcode.make(qr_data)

    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    qr_img = Image(buf, 12*mm, 12*mm)

    qr_box = Table([
        [qr_img],
        [Paragraph("SCAN", id_style)]
    ], colWidths=[16*mm])

    qr_box.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOX", (0,0), (-1,0), 0.5, gold),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))

    # ======================
    # 📄 CONTENU
    # ======================
    content = [
        [logo],
        [Paragraph("<b>HexaQuébec</b>", title_style)],
        [Paragraph("Solutions digitales", subtitle_style)],
        [Paragraph(safe(client.entreprise), info_style)],
        [Paragraph(safe(client.contact), info_style)],
        [Paragraph(safe(client.user.email), info_style)],
        [Paragraph(safe(client.adresse), info_style)],
        [Paragraph(f"ID : {safe(client.numero_client)}", id_style)],
    ]

    center_table = Table(content, colWidths=[48*mm])
    center_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0.5),
    ]))

    # ======================
    # 🧾 CARTE (réduite pour header)
    # ======================
    card = Table(
        [[center_table, qr_box]],
        colWidths=[54*mm, 18*mm],
        rowHeights=[40*mm]  # 🔥 réduit pour laisser place au titre
    )

    card.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    # ======================
    # 📌 ELEMENTS (1 seule page)
    # ======================
    elements = [
        Paragraph("CARTE D’AFFAIRE CLIENT", header_style),
        Spacer(1, 1),  # 🔥 très petit
        card
    ]

    # ======================
    # 🎨 DESIGN
    # ======================
    def draw(canvas, doc):

        canvas.setFillColor(colors.HexColor("#0B0F19"))
        canvas.rect(0, 0, width, height, fill=1)

        canvas.setFillColor(colors.HexColor("#111827"))
        canvas.rect(0, 0, 5, height, fill=1)

        canvas.setFillColor(gold)
        canvas.rect(5, height-4, width-10, 1.2, fill=1)

        canvas.setStrokeColor(gold)
        canvas.setLineWidth(0.8)
        canvas.roundRect(2, 2, width-4, height-4, 5)

    doc.build(elements, onFirstPage=draw)

    return response







from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from .models import Devis

def devis_view(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        service = request.POST.get("service")
        type_projet = request.POST.get("type_projet")
        description = request.POST.get("description")
        fichier = request.FILES.get("fichier")

        # 🔹 Sauvegarde DB
        Devis.objects.create(
            nom=nom,
            email=email,
            service=service,
            type_projet=type_projet,
            description=description,
            fichier=fichier
        )

        # 🔹 Traduction service
        services_dict = {
            "web": "Développement Web",
            "mobile": "Application Mobile",
            "ia": "Intelligence Artificielle",
            "maintenance": "Maintenance"
        }
        service_label = services_dict.get(service, service)

        # 🔥 EMAIL MODERNE HTML
        subject = "🚀 Confirmation de votre demande - HexaQuébec"

        html_content = f"""
        <div style="font-family:Arial;background:#f4f6f9;padding:20px;">
            <div style="max-width:600px;margin:auto;background:white;border-radius:15px;overflow:hidden;box-shadow:0 5px 20px rgba(0,0,0,0.1);">
                
                <div style="background:#0b132b;color:white;padding:20px;text-align:center;">
                    <h2 style="margin:0;color:#c6a87d;">HexaQuébec</h2>
                    <p style="margin:0;font-size:14px;">Solutions digitales modernes</p>
                </div>

                <div style="padding:25px;">
                    <h3>Bonjour {nom} 👋</h3>

                    <p>Merci pour votre demande de devis. Voici les informations :</p>

                    <div style="background:#f9fafb;padding:15px;border-radius:10px;">
                        <p><strong>Email :</strong> {email}</p>
                        <p><strong>Service :</strong> {service_label}</p>
                        <p><strong>Type de projet :</strong> {type_projet}</p>
                        <p><strong>Description :</strong> {description}</p>
                    </div>

                    <p style="margin-top:20px;">
                        ⏱️ Notre équipe vous répond sous 24h.
                    </p>

                    <div style="text-align:center;margin-top:20px;">
                        <a href="https://hexaquebec.com" 
                        style="background:#c6a87d;color:black;padding:12px 20px;border-radius:25px;text-decoration:none;">
                        🌐 Visiter notre site
                        </a>
                    </div>
                </div>

                <div style="background:#0b132b;color:#aaa;text-align:center;padding:15px;font-size:12px;">
                    © 2026 HexaQuébec
                </div>
            </div>
        </div>
        """

        email_message = EmailMultiAlternatives(
            subject,
            "",
            "hexaquebec80@gmail.com",
            [email],
        )

        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return redirect('devissucc')

    # ⚠️ CORRECTION ICI
    return render(request, "devis.html")



def devissucc(request):
    return render(request, 'devissucc.html')


import json
from django.http import JsonResponse
from .models import Payment

@login_required
def payment_successclient(request):
    if request.method == "POST":
        data = json.loads(request.body)

        Payment.objects.create(
            client=request.user.client,
            amount=request.session.get("payment_amount", 0),
            paypal_order_id=data["orderID"],
            status="paid"
        )

        return JsonResponse({"status": "ok"})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def paiement_client_view(request):
    if request.method == "POST":
        amount = request.POST.get("amount")

        if not amount:
            return redirect("payment_form")

        request.session['payment_amount'] = amount

        return render(request, "payment_page.html", {
            "amount": amount
        })

    return render(request, "payment_form.html")





@login_required
def paypal_checkout_view(request):
    return render(request, "paypal_checkout.html")




from django.contrib.auth.decorators import login_required

@login_required
def paypal_payment_view(request):
    if request.method == "POST":
        amount = request.POST.get("amount")

        # 🔐 validation sécurité
        if not amount:
            return redirect("paypal_checkout")

        try:
            amount = float(amount)
        except ValueError:
            return redirect("paypal_checkout")

        if amount <= 0:
            return redirect("paypal_checkout")

        # 💾 session sécurisée
        request.session["paypal_amount"] = str(amount)

        return render(request, "paypal_payment.html", {
            "amount": amount
        })

    return redirect("paypal_checkout")



@login_required
def paypal_success_view(request):
    amount = request.session.get("paypal_amount")

    return render(request, "paypal_success.html", {
        "amount": amount
    })

def paypal_error_view(request):
    return render(request, "paypal_error.html")

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Payment

@csrf_exempt
@login_required
def paypal_verify(request):

    data = json.loads(request.body)

    status = data.get("status")
    transaction_id = data.get("transaction_id")
    amount = data.get("amount")

    # ✅ Enregistrer en base (TOUJOURS)
    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        transaction_id=transaction_id,
        status=status
    )

    # ✅ LOGIQUE CORRECTE
    if status == "COMPLETED":
        return JsonResponse({"ok": True})
    else:
        return JsonResponse({
            "ok": False,
            "status": status
        })
    



    from django.shortcuts import render

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Announcement

def annonce_create(request):

    if request.method == "POST":

        annonce = Announcement.objects.create(
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            image=request.FILES.get("image"),
            author=request.user,
            published="published" in request.POST,
            published_at=timezone.now() if "published" in request.POST else None
        )

        return redirect("home")  # 🔥 ICI IMPORTANT

    return render(request, "annonce_create.html")


def annonce_list(request):
    annonces = Announcement.objects.all().order_by('-created_at')
    return render(request, "annonce_list.html", {
        "annonces": annonces
    })

@login_required
def video_create(request):

    if request.method == "POST":
        VideoAnnonce.objects.create(
            titre=request.POST['titre'],
            video=request.FILES['video']
        )
        return redirect('video_list')

    return render(request, "videos/video_create.html")

@login_required
def video_list(request):
    videos = VideoAnnonce.objects.all().order_by('-date_pub')
    return render(request, "videos/video_list.html", {
        "videos": videos
    })

@login_required
def affiche_create(request):

    if request.method == "POST":
        Affiche.objects.create(
            titre=request.POST['titre'],
            image=request.FILES['image']
        )
        return redirect('affiche_list')

    return render(request, "affiches/affiche_create.html")

@login_required
def affiche_list(request):
    affiches = Affiche.objects.filter(actif=True).order_by('-date_pub')
    return render(request, "affiches/affiche_list.html", {
        "affiches": affiches
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import PaiementClient



@login_required
def paye_dashboard(request):

    clients_paye = PaiementClient.objects.all().order_by('-date')

    total_revenus = PaiementClient.objects.filter(statut='paye').aggregate(
        total=Sum('montant')
    )['total'] or 0

    total_non_paye = PaiementClient.objects.filter(statut='non_paye').aggregate(
        total=Sum('montant')
    )['total'] or 0

    return render(request, "dashboard_hexa.html", {
        "clients_paye": clients_paye,
        "total_revenus": total_revenus,
        "total_non_paye": total_non_paye,
    })
# CREATE
def ajouter_paye(request):
    if request.method == "POST":
        PaiementClient.objects.create(
            nom_client=request.POST['nom_client'],
            entreprise=request.POST['entreprise'],
            telephone=request.POST['telephone'],
            residence=request.POST['residence'],
            titre_projet=request.POST['titre_projet'],
            montant=request.POST['montant'],
            statut=request.POST['statut'],
        )
        return redirect('paye_dashboard')

    return render(request, "paye_form.html")


# UPDATE
def modifier_paye(request, id):
    client = get_object_or_404(PaiementClient, id=id)

    if request.method == "POST":
        client.nom_client = request.POST['nom_client']
        client.entreprise = request.POST['entreprise']
        client.telephone = request.POST['telephone']
        client.residence = request.POST['residence']
        client.titre_projet = request.POST['titre_projet']
        client.montant = request.POST['montant']
        client.statut = request.POST['statut']
        client.save()
        return redirect('paye_dashboard')

    return render(request, "paye_form.html", {"client": client})


# DELETE
def supprimer_paye(request, id):
    client = get_object_or_404(PaiementClient, id=id)
    client.delete()
    return redirect('paye_dashboard')









def annonce_edit(request, id):
    annonce = get_object_or_404(Announcement, id=id)

    if request.method == "POST":
        annonce.title = request.POST['title']
        annonce.content = request.POST['content']

        if 'published' in request.POST:
            annonce.published = True
        else:
            annonce.published = False

        if request.FILES.get('image'):
            annonce.image = request.FILES['image']

        annonce.save()
        return redirect('annonces_list')

    return render(request, 'annonce_edit.html', {'annonce': annonce})




from django.shortcuts import render, redirect
from .models import Projet



def projet_list(request):

    projets = Projet.objects.all().order_by('-id')

    return render(request,
    'projets.html',
    {
        'projets': projets
    })


def ajouter_projet(request):

    if request.method == 'POST':

        Projet.objects.create(

            nom_projet=request.POST.get('nom_projet'),

            client=request.POST.get('client'),

            prix=request.POST.get('prix'),

            statut=request.POST.get('statut'),

            technologie=request.POST.get('technologie'),

            description=request.POST.get('description'),

            image=request.FILES.get('image')

        )

        return redirect('projet_list')

    return redirect('projet_list')

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404

# MODIFIER PROJET
def modifier_projet(request, id):

    projet = get_object_or_404(Projet, id=id)

    if request.method == "POST":

        projet.nom_projet = request.POST.get('nom_projet')
        projet.client = request.POST.get('client')

        # CORRECTION PRIX
        prix = request.POST.get('prix')

        if prix and prix.strip() != "":
            projet.prix = Decimal(prix)
        else:
            projet.prix = 0

        projet.technologie = request.POST.get('technologie')
        projet.statut = request.POST.get('statut')
        projet.description = request.POST.get('description')

        if request.FILES.get('image'):
            projet.image = request.FILES.get('image')

        projet.save()

        return redirect('projet_list')

    return render(request, 'modifier_projet.html', {
        'projet': projet
    })

# SUPPRIMER PROJET
def supprimer_projet(request, id):

    projet = get_object_or_404(Projet, id=id)

    projet.delete()











from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@csrf_exempt
def diam_ai_chat(request):

    if request.method == "POST":

        data = json.loads(request.body)
        question = data.get("message", "")

        system_prompt = """
        Tu es Diam AI, assistant virtuel officiel de HexaQuébec.

        Tu réponds toujours en français, de manière professionnelle, claire et intelligente.

        Informations HexaQuébec :
        - HexaQuébec fait du développement web
        - Création de sites vitrines
        - Création de sites e-commerce
        - Dashboards administratifs
        - Applications mobiles
        - Intelligence artificielle
        - Chatbots intelligents
        - UI/UX Design
        - Maintenance informatique
        - Stages disponibles : développement web, mobile, UI/UX, IA, infographie,administration
        - Réseau et cybersécurité non acceptés
        - Contact : hexaquebec80@gmail.com
        - Téléphone : +1 514 467 7377
        - Adresse : 2186 Rue Roussel, Chicoutimi, QC G7G 1W6

        Si la personne demande un prix, explique que le prix dépend du projet et propose de demander un devis.
        Si la personne demande un stage, explique les domaines acceptés et invite à remplir une demande de stage.
        Si la question n’a pas rapport avec HexaQuébec, réponds poliment et ramène vers les services HexaQuébec.
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = completion.choices[0].message.content

        return JsonResponse({
            "answer": answer
        })

    return JsonResponse({
        "answer": "Méthode non autorisée"
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GroupeStagiaire, MessageGroupeStagiaire, ReactionMessage, MessageLu, ProfilStagiaire

@login_required(login_url="login")
def reaction_message(request, message_id):
    message = get_object_or_404(MessageGroupeStagiaire, id=message_id)

    emoji = request.POST.get("emoji", "👍")

    ReactionMessage.objects.create(
        message=message,
        user=request.user,
        emoji=emoji
    )

    return redirect("groupe_stagiaires")

from django.shortcuts import render, redirect
from django.contrib import messages
def login_groupe_stagiaire(request):

    if request.method == "POST":
        email = request.POST.get("email")
        code_stagiaire = request.POST.get("code_stagiaire")

        try:
            login = Stagiairelogin.objects.get(
                email=email,
                code=code_stagiaire
            )

            profil, created = ProfilStagiaire.objects.get_or_create(
                stagiaire=login.stagiaire
            )

            request.session["profil_groupe_id"] = profil.id

            return redirect("groupe_stagiaires_stagiaire")

        except Stagiairelogin.DoesNotExist:
            messages.error(request, "Email ou code stagiaire incorrect.")

    return render(request, "login_groupe_stagiaire.html")


def logout_groupe_stagiaire(request):
    request.session.pop("profil_groupe_id", None)
    return redirect("login_groupe_stagiaire")

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone


@login_required(login_url="login")
def groupe_stagiaires_admin(request):

    groupe, created = GroupeStagiaire.objects.get_or_create(
        nom="Groupe Stagiaires"
    )

    stagiaires = ProfilStagiaire.objects.select_related("stagiaire").all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "ajouter":
            profil_id = request.POST.get("profil_id")
            profil = get_object_or_404(ProfilStagiaire, id=profil_id)
            groupe.stagiaires.add(profil)
            return redirect("groupe_stagiaires_admin")

        elif action == "retirer":
            profil_id = request.POST.get("profil_id")
            profil = get_object_or_404(ProfilStagiaire, id=profil_id)
            groupe.stagiaires.remove(profil)
            return redirect("groupe_stagiaires_admin")

        elif action == "message":
            texte = request.POST.get("message")
            fichier = request.FILES.get("fichier")

            if texte or fichier:
                MessageGroupeStagiaire.objects.create(
                    groupe=groupe,
                    auteur=request.user,
                    message=texte,
                    fichier=fichier
                )

                emails = list(
                    groupe.stagiaires
                    .exclude(stagiaire__email__isnull=True)
                    .exclude(stagiaire__email="")
                    .values_list("stagiaire__email", flat=True)
                    .distinct()
                )

                if emails:
                    lien = request.build_absolute_uri(
                        "/login-groupe-stagiaire/"
                    )

                    sujet = "Nouveau message dans le groupe HexaQuébec"

                    texte_simple = (
                        "Bonjour,\n\n"
                        "Vous avez reçu un nouveau message dans le groupe des stagiaires HexaQuébec.\n\n"
                        f"Connectez-vous ici : {lien}\n\n"
                        "Merci,\n"
                        "HexaQuébec"
                    )

                    html_message = f"""
                    <div style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,sans-serif;">
                        <div style="max-width:620px;margin:30px auto;background:#ffffff;border-radius:22px;overflow:hidden;box-shadow:0 18px 45px rgba(0,0,0,0.12);">

                            <div style="background:linear-gradient(135deg,#071a3d,#0057ff);padding:34px 28px;color:white;text-align:center;">
                                <h1 style="margin:0;font-size:26px;font-weight:900;">
                                    HexaQuébec
                                </h1>
                                <p style="margin:8px 0 0;font-size:15px;opacity:0.9;">
                                    Groupe des stagiaires
                                </p>
                            </div>

                            <div style="padding:32px 28px;color:#1f2937;">
                                <h2 style="margin:0 0 14px;font-size:22px;color:#071a3d;">
                                    Nouveau message reçu
                                </h2>

                                <p style="font-size:16px;line-height:1.7;margin:0 0 18px;">
                                    Bonjour,
                                </p>

                                <p style="font-size:16px;line-height:1.7;margin:0 0 18px;">
                                    Vous avez reçu un nouveau message dans le groupe des stagiaires
                                    <strong>HexaQuébec</strong>.
                                </p>

                                <div style="background:#f1f5ff;border-left:5px solid #0057ff;border-radius:14px;padding:16px 18px;margin:24px 0;">
                                    <p style="margin:0;color:#334155;font-size:15px;line-height:1.6;">
                                        Connectez-vous à votre espace stagiaire pour consulter le message et répondre dans le groupe.
                                    </p>
                                </div>

                                <div style="text-align:center;margin:30px 0;">
                                    <a href="{lien}"
                                       style="display:inline-block;background:linear-gradient(135deg,#0057ff,#003bb5);color:#ffffff;text-decoration:none;padding:15px 26px;border-radius:14px;font-weight:800;font-size:15px;">
                                        Consulter le message
                                    </a>
                                </div>

                                <p style="font-size:14px;color:#64748b;line-height:1.6;margin-top:24px;">
                                    Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
                                    <a href="{lien}" style="color:#0057ff;">{lien}</a>
                                </p>
                            </div>

                            <div style="background:#f8fafc;padding:18px 28px;text-align:center;border-top:1px solid #e5e7eb;">
                                <p style="margin:0;color:#64748b;font-size:13px;">
                                    © HexaQuébec — Communication interne des stagiaires
                                </p>
                            </div>

                        </div>
                    </div>
                    """

                    email = EmailMultiAlternatives(
                        subject=sujet,
                        body=texte_simple,
                        from_email=settings.EMAIL_HOST_USER,
                        to=emails
                    )

                    email.attach_alternative(html_message, "text/html")
                    email.send(fail_silently=False)

                    messages.success(
                        request,
                        "Message envoyé et courriel professionnel envoyé aux stagiaires."
                    )
                else:
                    messages.warning(
                        request,
                        "Message envoyé, mais aucun email stagiaire trouvé."
                    )

            return redirect("groupe_stagiaires_admin")

        elif action == "supprimer_message":
            message_id = request.POST.get("message_id")

            msg = get_object_or_404(
                MessageGroupeStagiaire,
                id=message_id,
                groupe=groupe
            )

            msg.supprime = True
            msg.supprime_par = request.user.username
            msg.date_suppression = timezone.now()
            msg.message = ""

            if msg.fichier:
                msg.fichier.delete(save=False)
                msg.fichier = None

            msg.save()

            return redirect("groupe_stagiaires_admin")

    return render(request, "groupe_stagiaires.html", {
        "groupe": groupe,
        "stagiaires": stagiaires,
        "messages_groupe": groupe.messages.all().order_by("date"),
        "is_admin": True,
    })




from django.utils import timezone

def groupe_stagiaires_stagiaire(request):

    profil_id = request.session.get("profil_groupe_id")

    if not profil_id:
        return redirect("login_groupe_stagiaire")

    profil = get_object_or_404(ProfilStagiaire, id=profil_id)

    groupe = GroupeStagiaire.objects.filter(stagiaires=profil).first()

    if not groupe:
        messages.error(request, "Vous n'êtes pas encore ajouté au groupe.")
        return redirect("login_groupe_stagiaire")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "supprimer_message":
            message_id = request.POST.get("message_id")

            msg = get_object_or_404(
                MessageGroupeStagiaire,
                id=message_id,
                groupe=groupe
            )

            msg.supprime = True
            msg.supprime_par = profil.stagiaire.nom
            msg.date_suppression = timezone.now()
            msg.message = ""

            if msg.fichier:
                msg.fichier.delete(save=False)
                msg.fichier = None

            msg.save()

            return redirect("groupe_stagiaires_stagiaire")

        else:
            texte = request.POST.get("message")
            fichier = request.FILES.get("fichier")

            if texte or fichier:
                MessageGroupeStagiaire.objects.create(
                    groupe=groupe,
                    auteur=request.user,
                    message=f"[STG-{profil.stagiaire.code}] {profil.stagiaire.nom} : {texte}",
                    fichier=fichier
                )

            return redirect("groupe_stagiaires_stagiaire")

    return render(request, "groupe_stagiaires.html", {
        "groupe": groupe,
        "messages_groupe": groupe.messages.all(),
        "profil": profil,
        "is_admin": False,
        "profil_code_tag": f"[STG-{profil.stagiaire.code}]",
    })



@login_required(login_url="login")
def groupe_stagiaires(request):

    groupe, created = GroupeStagiaire.objects.get_or_create(
        nom="Groupe Stagiaires"
    )

    stagiaires = ProfilStagiaire.objects.select_related("stagiaire").all()
    messages_groupe = groupe.messages.all().order_by("date")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "ajouter":
            profil_id = request.POST.get("profil_id")
            profil = get_object_or_404(ProfilStagiaire, id=profil_id)
            groupe.stagiaires.add(profil)
            return redirect("groupe_stagiaires")

        elif action == "retirer":
            profil_id = request.POST.get("profil_id")
            profil = get_object_or_404(ProfilStagiaire, id=profil_id)
            groupe.stagiaires.remove(profil)
            return redirect("groupe_stagiaires")

        elif action == "message":
            texte = request.POST.get("message")
            fichier = request.FILES.get("fichier")

            if texte or fichier:
                MessageGroupeStagiaire.objects.create(
                    groupe=groupe,
                    auteur=request.user,
                    message=texte,
                    fichier=fichier
                )

            return redirect("groupe_stagiaires")

        elif action == "supprimer_message":
            message_id = request.POST.get("message_id")

            msg = get_object_or_404(
                MessageGroupeStagiaire,
                id=message_id,
                groupe=groupe
            )

            msg.supprime = True
            msg.supprime_par = request.user.username
            msg.date_suppression = timezone.now()
            msg.message = ""

            if msg.fichier:
                msg.fichier.delete(save=False)
                msg.fichier = None

            msg.save()

            return redirect("groupe_stagiaires")

    return render(request, "groupe_stagiaires.html", {
        "groupe": groupe,
        "stagiaires": stagiaires,
        "messages_groupe": messages_groupe,
        "is_admin": True,
    })

   


import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect


@login_required(login_url="login")
def lancer_appel_video_groupe(request):

    groupe, created = GroupeStagiaire.objects.get_or_create(
        nom="Groupe Stagiaires"
    )

    room_id = f"hexaquebec-stagiaires-{uuid.uuid4().hex[:10]}"
    lien_appel = f"https://meet.jit.si/{room_id}"

    MessageGroupeStagiaire.objects.create(
        groupe=groupe,
        auteur=request.user,
        message=(
            "📹 Appel vidéo lancé par l'admin.\n\n"
            f"Rejoindre l'appel : {lien_appel}"
        )
    )

    emails = list(
        groupe.stagiaires
        .exclude(stagiaire__email__isnull=True)
        .exclude(stagiaire__email="")
        .values_list("stagiaire__email", flat=True)
        .distinct()
    )

    if emails:
        sujet = "📹 Appel vidéo HexaQuébec"

        texte_simple = (
            "Bonjour,\n\n"
            "Un appel vidéo vient d'être lancé dans le groupe des stagiaires HexaQuébec.\n\n"
            f"Rejoindre l'appel vidéo : {lien_appel}\n\n"
            "Merci,\n"
            "HexaQuébec"
        )

        html_message = f"""
        <div style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,sans-serif;">
            <div style="max-width:650px;margin:30px auto;background:#ffffff;border-radius:24px;overflow:hidden;box-shadow:0 18px 45px rgba(0,0,0,0.15);">

                <div style="background:linear-gradient(135deg,#071a3d,#0057ff);padding:36px 28px;color:white;text-align:center;">
                    <h1 style="margin:0;font-size:28px;font-weight:900;">
                        📹 Appel vidéo HexaQuébec
                    </h1>
                    <p style="margin:10px 0 0;font-size:15px;opacity:0.9;">
                        Groupe des stagiaires
                    </p>
                </div>

                <div style="padding:34px 30px;color:#1f2937;">
                    <h2 style="margin:0 0 16px;font-size:22px;color:#071a3d;">
                        Un appel vidéo vient d'être lancé
                    </h2>

                    <p style="font-size:16px;line-height:1.7;margin:0 0 18px;">
                        Bonjour,
                    </p>

                    <p style="font-size:16px;line-height:1.7;margin:0 0 18px;">
                        L'administration <strong>HexaQuébec</strong> a lancé un appel vidéo
                        dans le groupe des stagiaires.
                    </p>

                    <div style="background:#ecfdf5;border-left:5px solid #16a34a;border-radius:16px;padding:18px;margin:26px 0;">
                        <p style="margin:0;color:#065f46;font-size:15px;line-height:1.6;font-weight:700;">
                            Cliquez sur le bouton ci-dessous pour rejoindre directement la réunion vidéo.
                        </p>
                    </div>

                    <div style="text-align:center;margin:34px 0;">
                        <a href="{lien_appel}"
                           style="display:inline-block;background:linear-gradient(135deg,#16a34a,#22c55e);color:#ffffff;text-decoration:none;padding:16px 30px;border-radius:15px;font-weight:900;font-size:15px;">
                            Rejoindre l'appel vidéo
                        </a>
                    </div>

                    <p style="font-size:14px;color:#64748b;line-height:1.6;margin-top:24px;">
                        Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
                        <a href="{lien_appel}" style="color:#16a34a;font-weight:700;">
                            {lien_appel}
                        </a>
                    </p>
                </div>

                <div style="background:#f8fafc;padding:18px 28px;text-align:center;border-top:1px solid #e5e7eb;">
                    <p style="margin:0;color:#64748b;font-size:13px;">
                        © HexaQuébec — Communication interne des stagiaires
                    </p>
                </div>

            </div>
        </div>
        """

        email = EmailMultiAlternatives(
            subject=sujet,
            body=texte_simple,
            from_email=settings.EMAIL_HOST_USER,
            to=emails
        )

        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        messages.success(
            request,
            "Appel vidéo lancé et courriel envoyé aux stagiaires."
        )
    else:
        messages.warning(
            request,
            "Appel vidéo lancé, mais aucun email stagiaire trouvé."
        )

    return redirect("groupe_stagiaires_admin")


def a_propos(request):
    return render(request, "a_propos.html")




@login_required(login_url="login")
def telecharger_attestation(request, profil_id):
    profil = get_object_or_404(ProfilStagiaire, id=profil_id)

    if not profil.stage_valide:
        messages.error(request, "Le stage n'est pas encore validé.")
        return redirect("groupe_stagiaires_admin")

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    bleu = colors.HexColor("#071A3D")
    bleu2 = colors.HexColor("#0057FF")
    gris = colors.HexColor("#F4F7FC")
    texte = colors.HexColor("#1F2937")
    gold = colors.HexColor("#D4AF37")

    title_style = ParagraphStyle(
        "TitleModern",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=26,
        textColor=bleu,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "SubtitleModern",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        leading=16,
        textColor=texte
    )

    normal_style = ParagraphStyle(
        "NormalModern",
        parent=styles["Normal"],
        fontSize=11,
        leading=18,
        textColor=texte,
        alignment=TA_CENTER
    )

    name_style = ParagraphStyle(
        "NameStyle",
        parent=styles["Title"],
        fontSize=20,
        alignment=TA_CENTER,
        textColor=bleu2,
        leading=24
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#6B7280")
    )

    elements = []

    # ================= HEADER =================
    logo_path = os.path.join(settings.STATIC_ROOT, "images/logoHexa.png")

    header_content = []

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=120, height=60)
        header_content.append([logo])

    header_content += [
        [Paragraph("<b>HEXACQUÉBEC</b>", ParagraphStyle(
            "Company",
            parent=styles["Title"],
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.white
        ))],
        [Paragraph(
            "Développement Web & Mobile • Intelligence Artificielle • Maintenance Informatique",
            ParagraphStyle(
                "CompanySub",
                parent=styles["Normal"],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.white
            )
        )],
    ]

    header = Table(header_content, colWidths=[500])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bleu),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 1, bleu),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 22))

    # ================= TITRE =================
    elements.append(Paragraph("ATTESTATION DE STAGE", title_style))
    elements.append(Paragraph("Document officiel délivré par HexaQuébec", subtitle_style))

    elements.append(Spacer(1, 15))

    line = Table([[""]], colWidths=[500])
    line.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 2, gold),
    ]))
    elements.append(line)

    elements.append(Spacer(1, 25))

    # ================= CONTENU =================
    elements.append(Paragraph("Nous attestons par la présente que :", normal_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph(f"<b>{profil.stagiaire.nom}</b>", name_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"a effectué un stage en <b>{profil.stagiaire.specialite}</b> au sein de notre entreprise.",
        normal_style
    ))

    elements.append(Spacer(1, 20))

    date_debut = profil.date_debut.strftime("%d/%m/%Y") if profil.date_debut else ""
    date_fin = profil.date_fin.strftime("%d/%m/%Y") if profil.date_fin else "En cours"

    infos = Table([
        ["Code stagiaire", profil.code_stagiaire],
        ["Période du stage", f"Du {date_debut} au {date_fin}"],
        ["Lieu", "Chicoutimi, Québec, Canada"],
        ["Statut", "Stage validé"],
    ], colWidths=[170, 280])

    infos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), gris),
        ("TEXTCOLOR", (0, 0), (0, -1), bleu),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D9E2F1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F1")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))

    elements.append(infos)

    elements.append(Spacer(1, 22))

    elements.append(Paragraph(
        "Durant cette période, le stagiaire a fait preuve de sérieux, de professionnalisme, "
        "d’adaptation et d’engagement dans les missions confiées.",
        normal_style
    ))

    elements.append(Spacer(1, 25))

    # ================= ÉVALUATION =================
    evaluation = Table([
        ["Compétences techniques", "Très satisfaisant"],
        ["Organisation", "Très satisfaisant"],
        ["Esprit d’équipe", "Excellent"],
        ["Professionnalisme", "Excellent"],
    ], colWidths=[250, 200])

    evaluation.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (0, -1), bleu),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D9E2F1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F1")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))

    elements.append(evaluation)

    elements.append(Spacer(1, 30))

    # ================= SIGNATURE =================
    responsable = profil.responsable or "Responsable HexaQuébec"

    signature_table = Table([
        [
            Paragraph(
                f"Fait à Chicoutimi, Québec<br/><br/><b>{responsable}</b><br/>Responsable du stage",
                normal_style
            ),
            Paragraph(
                f"<b>N° Attestation</b><br/>{profil.code_stagiaire}<br/><br/>NEQ : 2281156671",
                small_style
            )
        ]
    ], colWidths=[280, 180])

    signature_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (1, 0), (1, 0), 1, gold),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FFF8E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))

    elements.append(signature_table)

    # ================= FOND / BORDURE =================
    def draw(canvas, doc):
        width, height = LETTER

        canvas.setFillColor(bleu)
        canvas.rect(0, height - 18, width, 18, fill=1, stroke=0)

        canvas.setFillColor(bleu2)
        canvas.rect(0, height - 22, width, 4, fill=1, stroke=0)

        canvas.setStrokeColor(bleu)
        canvas.setLineWidth(2)
        canvas.roundRect(20, 20, width - 40, height - 40, 12, stroke=1, fill=0)

        canvas.setStrokeColor(gold)
        canvas.setLineWidth(1)
        canvas.roundRect(30, 30, width - 60, height - 60, 8, stroke=1, fill=0)

        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(
            width / 2,
            18,
            "HexaQuébec — Attestation officielle de stage"
        )

    doc.build(elements, onFirstPage=draw)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="attestation_{profil.code_stagiaire}.pdf"'

    return response





from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import AttestationStageForm
from .models import AttestationStage


@login_required
def liste_attestations_stagiaires(request):

    attestations = AttestationStage.objects.filter(
        actif=True,
    ).select_related(
        "cree_par",
    )

    recherche = request.GET.get(
        "q",
        "",
    ).strip()

    if recherche:

        attestations = attestations.filter(
            Q(
                numero_attestation__icontains=recherche,
            )
            |
            Q(
                numero_stagiaire__icontains=recherche,
            )
            |
            Q(
                nom__icontains=recherche,
            )
            |
            Q(
                prenom__icontains=recherche,
            )
            |
            Q(
                programme__icontains=recherche,
            )
        )

    context = {
        "attestations": attestations,
        "recherche": recherche,
    }

    return render(
        request,
        "liste_attestations.html",
        context,
    )


@login_required
def creer_attestation_stagiaire(request):

    if request.method == "POST":

        form = AttestationStageForm(
            request.POST,
        )

        if form.is_valid():

            attestation = form.save(
                commit=False,
            )

            attestation.cree_par = request.user
            attestation.save()

            messages.success(
                request,
                (
                    "L’attestation de stage a été "
                    "créée avec succès."
                ),
            )

            return redirect(
                "detail_attestation_stagiaire",
                pk=attestation.pk,
            )

    else:

        valeurs_initiales = {}

        nom_utilisateur = (
            request.user.get_full_name().strip()
        )

        if nom_utilisateur:

            valeurs_initiales["responsable"] = (
                nom_utilisateur
            )

        form = AttestationStageForm(
            initial=valeurs_initiales,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "creer_attestation.html",
        context,
    )


@login_required
def detail_attestation_stagiaire(
    request,
    pk,
):

    attestation = get_object_or_404(
        AttestationStage.objects.select_related(
            "cree_par",
        ),
        pk=pk,
        actif=True,
    )

    context = {
        "attestation": attestation,
    }

    return render(
        request,
        "detail_attestation.html",
        context,
    )








def solutions_applications(request):
    type_selectionne = request.GET.get(
        "type",
        "restaurant",
    )

    qualite_selectionnee = request.GET.get(
        "qualite",
        "professionnel",
    )

    if type_selectionne not in CATALOGUE_APPLICATIONS:
        type_selectionne = "restaurant"

    if qualite_selectionnee not in [
        "essentiel",
        "professionnel",
        "premium",
    ]:
        qualite_selectionnee = "professionnel"

    if request.method == "POST":
        form = DemandeApplicationForm(request.POST)

        type_selectionne = request.POST.get(
            "type_application",
            "restaurant",
        )

        qualite_selectionnee = request.POST.get(
            "qualite",
            "professionnel",
        )

        if form.is_valid():
            application = CATALOGUE_APPLICATIONS.get(
                type_selectionne
            )

            if not application:
                form.add_error(
                    "type_application",
                    "Le type d’application est invalide.",
                )

            else:
                forfait = application["forfaits"].get(
                    qualite_selectionnee
                )

                if not forfait:
                    form.add_error(
                        "qualite",
                        "Le forfait sélectionné est invalide.",
                    )

                else:
                    demande = form.save(commit=False)

                    demande.nom_application = application["nom"]
                    demande.nom_forfait = forfait["nom"]
                    demande.prix_estime = forfait["prix"]
                    demande.devise = forfait.get(
                        "devise",
                        "CAD",
                    )
                    demande.delai_estime = forfait["delai"]
                    demande.fonctionnalites = forfait[
                        "fonctionnalites"
                    ]

                    demande.save()

                    try:
                        envoyer_emails_demande_application(
                            demande
                        )
                    except Exception:
                        logger.exception(
                            "Erreur pendant l’envoi de la demande %s",
                            demande.numero_demande,
                        )

                    return redirect(
                        "demande_application_succes",
                        token=demande.token_public,
                    )

    else:
        form = DemandeApplicationForm(
            initial={
                "type_application": type_selectionne,
                "qualite": qualite_selectionnee,
            }
        )

    # Mets le return render ici, à la fin de la fonction.
    return render(
        request,
        "solutions_applications.html",
        {
            "form": form,
            "catalogue": CATALOGUE_APPLICATIONS,
            "type_selectionne": type_selectionne,
            "qualite_selectionnee": qualite_selectionnee,
        },
    )


# La prochaine fonction commence après le return render.
def demande_application_succes(request, token):
    demande = get_object_or_404(
        DemandeApplication,
        token_public=token,
    )

    return render(
        request,
        "demande_application_succes.html",
        {
            "demande": demande,
        },
    )


def telecharger_demande_application_pdf(request, token):
    demande = get_object_or_404(
        DemandeApplication,
        token_public=token,
    )

    pdf = generer_pdf_demande(demande)

    response = HttpResponse(
        pdf,
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="'
        f'demande-{demande.numero_demande}.pdf"'
    )

    return response




import json
from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import logging

from xml.sax.saxutils import escape


def formater_prix(prix):
    """
    Formate un prix selon la présentation utilisée par HexaQuébec.

    Exemple :
        4500 -> 4 500 $ CAD
    """

    if prix is None:
        return "Sur devis"

    try:
        prix_formate = f"{float(prix):,.0f}".replace(",", " ")
    except (TypeError, ValueError):
        return "Sur devis"

    return f"{prix_formate} $ CAD"


def generer_pdf_demande(demande):
    """
    Génère un PDF professionnel contenant le résumé complet
    de la demande d’application du client.
    """

    buffer = BytesIO()

    # ============================================================
    # COULEURS HEXAQUÉBEC
    # ============================================================

    couleur_navy = colors.HexColor("#0B1F36")
    couleur_navy_clair = colors.HexColor("#153E5C")
    couleur_verte = colors.HexColor("#16A58D")
    couleur_verte_foncee = colors.HexColor("#0D7565")
    couleur_verte_claire = colors.HexColor("#EAF8F5")
    couleur_bleue_claire = colors.HexColor("#EEF5FF")
    couleur_fond = colors.HexColor("#F5F7FA")
    couleur_bordure = colors.HexColor("#DDE3EA")
    couleur_texte = colors.HexColor("#263449")
    couleur_gris = colors.HexColor("#667085")
    couleur_blanche = colors.white

    largeur_page, hauteur_page = A4

    # ============================================================
    # DOCUMENT
    # ============================================================

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=25 * mm,
        title=f"Demande {demande.numero_demande}",
        author="HexaQuébec",
        subject="Résumé d’une demande de développement numérique",
        creator="HexaQuébec",
    )

    styles = getSampleStyleSheet()

    # ============================================================
    # STYLES
    # ============================================================

    styles.add(
        ParagraphStyle(
            name="HexaMarque",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22,
            textColor=couleur_blanche,
            spaceAfter=3,
        )
    )

    styles.add(
        ParagraphStyle(
            name="HexaSlogan",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#D8E4EE"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="DocumentType",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=TA_RIGHT,
            textColor=couleur_blanche,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="DocumentReference",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#D8E4EE"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="TitrePrincipalHexa",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            alignment=TA_LEFT,
            textColor=couleur_navy,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="IntroductionHexa",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=couleur_gris,
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHexa",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=couleur_navy,
            spaceBefore=4,
            spaceAfter=0,
        )
    )

    styles.add(
        ParagraphStyle(
            name="LabelHexa",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=couleur_gris,
            spaceAfter=3,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ValeurHexa",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=couleur_texte,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ValeurSimpleHexa",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            textColor=couleur_texte,
        )
    )

    styles.add(
        ParagraphStyle(
            name="PrixHexa",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=23,
            alignment=TA_RIGHT,
            textColor=couleur_verte_foncee,
        )
    )

    styles.add(
        ParagraphStyle(
            name="PrixLabelHexa",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            alignment=TA_RIGHT,
            textColor=couleur_gris,
        )
    )

    styles.add(
        ParagraphStyle(
            name="FonctionnaliteHexa",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=13,
            textColor=couleur_texte,
        )
    )

    styles.add(
        ParagraphStyle(
            name="NoteHexa",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=13,
            textColor=couleur_texte,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ContactHexa",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=9,
            alignment=TA_CENTER,
            textColor=couleur_gris,
        )
    )

    styles.add(
        ParagraphStyle(
            name="PiedPageHexa",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=couleur_gris,
        )
    )

    styles.add(
        ParagraphStyle(
            name="PiedPageNumero",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            alignment=TA_RIGHT,
            textColor=couleur_gris,
        )
    )

    # ============================================================
    # FONCTIONS INTERNES
    # ============================================================

    def texte_securise(valeur, valeur_defaut="Non indiqué"):
        if valeur is None:
            return escape(valeur_defaut)

        valeur = str(valeur).strip()

        if not valeur:
            return escape(valeur_defaut)

        return escape(valeur)

    def paragraphe_valeur(valeur, style=None):
        return Paragraph(
            texte_securise(valeur),
            style or styles["ValeurSimpleHexa"],
        )

    def titre_section(titre):
        """
        Crée un titre de section avec une barre verte à gauche.
        """

        barre = Table(
            [
                [
                    "",
                    Paragraph(
                        escape(titre),
                        styles["SectionHexa"],
                    ),
                ]
            ],
            colWidths=[3 * mm, 153 * mm],
        )

        barre.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, 0),
                        couleur_verte,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (0, 0),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (0, 0),
                        0,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (0, 0),
                        0,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (0, 0),
                        0,
                    ),
                    (
                        "LEFTPADDING",
                        (1, 0),
                        (1, 0),
                        9,
                    ),
                    (
                        "RIGHTPADDING",
                        (1, 0),
                        (1, 0),
                        0,
                    ),
                    (
                        "TOPPADDING",
                        (1, 0),
                        (1, 0),
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (1, 0),
                        (1, 0),
                        4,
                    ),
                ]
            )
        )

        return barre

    def dessiner_pied_de_page(canvas, doc):
        """
        Ajoute les coordonnées et le numéro de page
        sur chaque page du PDF.
        """

        canvas.saveState()

        canvas.setStrokeColor(couleur_bordure)
        canvas.setLineWidth(0.6)

        canvas.line(
            17 * mm,
            18 * mm,
            largeur_page - 17 * mm,
            18 * mm,
        )

        canvas.setFillColor(couleur_navy)
        canvas.setFont("Helvetica-Bold", 7.5)

        canvas.drawString(
            17 * mm,
            12.5 * mm,
            "HexaQuébec",
        )

        canvas.setFillColor(couleur_gris)
        canvas.setFont("Helvetica", 6.8)

        canvas.drawString(
            39 * mm,
            12.5 * mm,
            "514 467 7377  |  hexaquebec80@gmail.com",
        )

        canvas.drawString(
            17 * mm,
            8.5 * mm,
            "2186, rue Roussel, Chicoutimi, QC, Canada",
        )

        canvas.setFillColor(couleur_gris)
        canvas.setFont("Helvetica-Bold", 7)

        canvas.drawRightString(
            largeur_page - 17 * mm,
            10.5 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    # ============================================================
    # DATE ET STATUT
    # ============================================================

    date_creation = demande.date_creation

    try:
        if timezone.is_aware(date_creation):
            date_creation = timezone.localtime(date_creation)
    except (TypeError, ValueError):
        pass

    date_formatee = date_creation.strftime(
        "%d/%m/%Y à %H:%M"
    )

    try:
        statut = demande.get_statut_display()
    except AttributeError:
        statut = getattr(
            demande,
            "statut",
            "Demande reçue",
        )

    # ============================================================
    # EN-TÊTE
    # ============================================================

    bloc_marque = Paragraph(
        (
            "HEXAQUÉBEC"
            "<br/>"
            "<font size='8'>"
            "Développement web, mobile et intelligence artificielle"
            "</font>"
        ),
        styles["HexaMarque"],
    )

    bloc_document = Paragraph(
        (
            "<b>DEMANDE DE DÉVELOPPEMENT</b>"
            "<br/>"
            f"<font size='8'>Référence : "
            f"{texte_securise(demande.numero_demande)}</font>"
        ),
        styles["DocumentType"],
    )

    entete = Table(
        [
            [
                bloc_marque,
                bloc_document,
            ]
        ],
        colWidths=[102 * mm, 54 * mm],
    )

    entete.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    couleur_navy,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (0, 0),
                    16,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (0, 0),
                    10,
                ),
                (
                    "LEFTPADDING",
                    (1, 0),
                    (1, 0),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (1, 0),
                    (1, 0),
                    16,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    15,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    15,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    4,
                    couleur_verte,
                ),
            ]
        )
    )

    # ============================================================
    # COORDONNÉES SOUS L’EN-TÊTE
    # ============================================================

    coordonnees = Table(
        [
            [
                Paragraph(
                    "<b>Téléphone</b><br/>514 467 7377",
                    styles["ContactHexa"],
                ),
                Paragraph(
                    "<b>Email</b><br/>hexaquebec80@gmail.com",
                    styles["ContactHexa"],
                ),
                Paragraph(
                    (
                        "<b>Adresse</b><br/>"
                        "2186, rue Roussel, Chicoutimi, QC, Canada"
                    ),
                    styles["ContactHexa"],
                ),
            ]
        ],
        colWidths=[
            44 * mm,
            52 * mm,
            60 * mm,
        ],
    )

    coordonnees.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    couleur_fond,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    couleur_bordure,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    couleur_bordure,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    # ============================================================
    # CARTE DE RÉFÉRENCE
    # ============================================================

    carte_reference = Table(
        [
            [
                Paragraph(
                    "NUMÉRO DE DEMANDE",
                    styles["LabelHexa"],
                ),
                Paragraph(
                    "DATE DE RÉCEPTION",
                    styles["LabelHexa"],
                ),
                Paragraph(
                    "STATUT",
                    styles["LabelHexa"],
                ),
            ],
            [
                Paragraph(
                    texte_securise(
                        demande.numero_demande
                    ),
                    styles["ValeurHexa"],
                ),
                Paragraph(
                    texte_securise(
                        date_formatee
                    ),
                    styles["ValeurHexa"],
                ),
                Paragraph(
                    texte_securise(
                        statut
                    ),
                    styles["ValeurHexa"],
                ),
            ],
        ],
        colWidths=[
            55 * mm,
            55 * mm,
            46 * mm,
        ],
    )

    carte_reference.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    couleur_fond,
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    couleur_blanche,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    couleur_bordure,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    couleur_bordure,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, 1),
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 1),
                    (-1, 1),
                    9,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    # ============================================================
    # INFORMATIONS DU CLIENT
    # ============================================================

    tableau_client = Table(
        [
            [
                Paragraph(
                    "Nom complet",
                    styles["LabelHexa"],
                ),
                paragraphe_valeur(
                    demande.nom_complet,
                    styles["ValeurHexa"],
                ),
            ],
            [
                Paragraph(
                    "Entreprise",
                    styles["LabelHexa"],
                ),
                paragraphe_valeur(
                    demande.nom_entreprise,
                    styles["ValeurHexa"],
                ),
            ],
            [
                Paragraph(
                    "Adresse email",
                    styles["LabelHexa"],
                ),
                paragraphe_valeur(
                    demande.email
                ),
            ],
            [
                Paragraph(
                    "Téléphone",
                    styles["LabelHexa"],
                ),
                paragraphe_valeur(
                    demande.telephone
                ),
            ],
        ],
        colWidths=[
            42 * mm,
            114 * mm,
        ],
    )

    tableau_client.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    couleur_fond,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    couleur_bordure,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    couleur_bordure,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    # ============================================================
    # SOLUTION SÉLECTIONNÉE
    # ============================================================

    informations_solution = Table(
        [
            [
                Paragraph(
                    "APPLICATION",
                    styles["LabelHexa"],
                ),
                Paragraph(
                    "NIVEAU DE QUALITÉ",
                    styles["LabelHexa"],
                ),
            ],
            [
                Paragraph(
                    texte_securise(
                        demande.nom_application
                    ),
                    styles["ValeurHexa"],
                ),
                Paragraph(
                    texte_securise(
                        demande.nom_forfait
                    ),
                    styles["ValeurHexa"],
                ),
            ],
            [
                Paragraph(
                    "DÉLAI INDICATIF",
                    styles["LabelHexa"],
                ),
                Paragraph(
                    "DÉLAI SOUHAITÉ PAR LE CLIENT",
                    styles["LabelHexa"],
                ),
            ],
            [
                Paragraph(
                    texte_securise(
                        demande.delai_estime
                    ),
                    styles["ValeurSimpleHexa"],
                ),
                Paragraph(
                    texte_securise(
                        demande.delai_souhaite
                    ),
                    styles["ValeurSimpleHexa"],
                ),
            ],
            [
                Paragraph(
                    "BUDGET PRÉVU",
                    styles["LabelHexa"],
                ),
                Paragraph(
                    "RÉFÉRENCE",
                    styles["LabelHexa"],
                ),
            ],
            [
                Paragraph(
                    texte_securise(
                        demande.budget_client
                    ),
                    styles["ValeurSimpleHexa"],
                ),
                Paragraph(
                    texte_securise(
                        demande.numero_demande
                    ),
                    styles["ValeurSimpleHexa"],
                ),
            ],
        ],
        colWidths=[
            55 * mm,
            55 * mm,
        ],
    )

    informations_solution.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    couleur_verte_claire,
                ),
                (
                    "BACKGROUND",
                    (0, 2),
                    (-1, 2),
                    couleur_verte_claire,
                ),
                (
                    "BACKGROUND",
                    (0, 4),
                    (-1, 4),
                    couleur_verte_claire,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#C8E6DF"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D7ECE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    carte_prix = Table(
        [
            [
                Paragraph(
                    "PRIX INDICATIF",
                    styles["PrixLabelHexa"],
                )
            ],
            [
                Paragraph(
                    (
                        "À partir de<br/>"
                        f"{escape(formater_prix(demande.prix_estime))}"
                    ),
                    styles["PrixHexa"],
                )
            ],
            [
                Paragraph(
                    (
                        "Le montant définitif sera confirmé "
                        "après l’analyse du projet."
                    ),
                    styles["ContactHexa"],
                )
            ],
        ],
        colWidths=[42 * mm],
    )

    carte_prix.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    couleur_verte_claire,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    couleur_verte,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    bloc_solution = Table(
        [
            [
                informations_solution,
                carte_prix,
            ]
        ],
        colWidths=[
            112 * mm,
            44 * mm,
        ],
    )

    bloc_solution.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (0, 0),
                    3,
                ),
                (
                    "LEFTPADDING",
                    (1, 0),
                    (1, 0),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (1, 0),
                    (1, 0),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    # ============================================================
    # FONCTIONNALITÉS
    # ============================================================

    fonctionnalites = demande.fonctionnalites or []

    if isinstance(fonctionnalites, str):
        try:
            fonctionnalites = json.loads(
                fonctionnalites
            )
        except (json.JSONDecodeError, TypeError):
            fonctionnalites = [
                fonctionnalites
            ]

    if not isinstance(fonctionnalites, list):
        fonctionnalites = list(
            fonctionnalites
        )

    lignes_fonctionnalites = []

    for fonctionnalite in fonctionnalites:
        lignes_fonctionnalites.append(
            [
                Paragraph(
                    "&#8226;",
                    ParagraphStyle(
                        name=f"PuceVerte{len(lignes_fonctionnalites)}",
                        parent=styles["Normal"],
                        fontName="Helvetica-Bold",
                        fontSize=13,
                        leading=13,
                        alignment=TA_CENTER,
                        textColor=couleur_verte,
                    ),
                ),
                Paragraph(
                    texte_securise(
                        fonctionnalite
                    ),
                    styles["FonctionnaliteHexa"],
                ),
            ]
        )

    if not lignes_fonctionnalites:
        lignes_fonctionnalites.append(
            [
                Paragraph(
                    "&#8226;",
                    styles["FonctionnaliteHexa"],
                ),
                Paragraph(
                    "Les fonctionnalités seront confirmées après analyse.",
                    styles["FonctionnaliteHexa"],
                ),
            ]
        )

    tableau_fonctionnalites = Table(
        lignes_fonctionnalites,
        colWidths=[
            8 * mm,
            148 * mm,
        ],
        splitByRow=1,
    )

    tableau_fonctionnalites.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    couleur_blanche,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (0, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (0, -1),
                    2,
                ),
                (
                    "LEFTPADDING",
                    (1, 0),
                    (1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (1, 0),
                    (1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.35,
                    colors.HexColor("#EEF1F4"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    couleur_bordure,
                ),
            ]
        )
    )

    # ============================================================
    # DESCRIPTION
    # ============================================================

    description = (
        demande.description.strip()
        if demande.description
        else "Aucune description supplémentaire n’a été fournie."
    )

    description_securisee = escape(
        description
    ).replace(
        "\n",
        "<br/>",
    )

    carte_description = Table(
        [
            [
                Paragraph(
                    description_securisee,
                    styles["ValeurSimpleHexa"],
                )
            ]
        ],
        colWidths=[156 * mm],
    )

    carte_description.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    couleur_fond,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    couleur_bordure,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    11,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    11,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ]
        )
    )

    # ============================================================
    # NOTE IMPORTANTE
    # ============================================================

    note_importante = Table(
        [
            [
                Paragraph(
                    "<b>IMPORTANT</b>",
                    ParagraphStyle(
                        name="TitreImportantHexa",
                        parent=styles["Normal"],
                        fontName="Helvetica-Bold",
                        fontSize=8,
                        leading=10,
                        textColor=couleur_navy,
                    ),
                ),
                Paragraph(
                    (
                        "Ce document confirme la réception de votre demande. "
                        "Il ne constitue pas un devis, une facture ou un contrat. "
                        "Le prix, le délai et les modalités définitives seront "
                        "confirmés après l’analyse complète du projet par HexaQuébec."
                    ),
                    styles["NoteHexa"],
                ),
            ]
        ],
        colWidths=[
            25 * mm,
            131 * mm,
        ],
    )

    note_importante.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    couleur_bleue_claire,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#D5E5FB"),
                ),
                (
                    "LINEBEFORE",
                    (0, 0),
                    (0, 0),
                    4,
                    colors.HexColor("#3478F6"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    # ============================================================
    # CONTENU FINAL
    # ============================================================

    contenu = [
        entete,
        coordonnees,
        Spacer(1, 15),

        Paragraph(
            "Résumé de votre demande",
            styles["TitrePrincipalHexa"],
        ),

        Paragraph(
            (
                "Merci d’avoir choisi HexaQuébec. Nous avons bien reçu "
                "votre demande de développement. Vous trouverez ci-dessous "
                "le résumé des informations transmises."
            ),
            styles["IntroductionHexa"],
        ),

        carte_reference,
        Spacer(1, 15),

        titre_section(
            "Informations du client"
        ),
        Spacer(1, 8),
        tableau_client,
        Spacer(1, 15),

        titre_section(
            "Solution numérique sélectionnée"
        ),
        Spacer(1, 8),
        bloc_solution,
        Spacer(1, 15),

        titre_section(
            "Fonctionnalités incluses"
        ),
        Spacer(1, 8),
        tableau_fonctionnalites,
        Spacer(1, 15),

        titre_section(
            "Description du projet"
        ),
        Spacer(1, 8),
        carte_description,
        Spacer(1, 16),

        note_importante,
        Spacer(1, 15),

        HRFlowable(
            width="100%",
            thickness=0.7,
            color=couleur_bordure,
            spaceBefore=2,
            spaceAfter=10,
        ),

        Paragraph(
            (
                "<b>Nous, HexaQuébec, avons reçu votre demande.</b><br/>"
                "Notre équipe communiquera avec vous après l’analyse "
                "des informations fournies."
            ),
            styles["NoteHexa"],
        ),

        Spacer(1, 8),

        Paragraph(
            (
                "<b>HexaQuébec</b><br/>"
                "Développement web, applications mobiles et intelligence artificielle<br/>"
                "Téléphone : 514 467 7377<br/>"
                "Email : hexaquebec80@gmail.com<br/>"
                "Adresse : 2186, rue Roussel, Chicoutimi, QC, Canada"
            ),
            styles["NoteHexa"],
        ),
    ]

    document.build(
        contenu,
        onFirstPage=dessiner_pied_de_page,
        onLaterPages=dessiner_pied_de_page,
    )

    resultat = buffer.getvalue()
    buffer.close()

    return resultat

def envoyer_emails_demande_application(demande):
    pdf = generer_pdf_demande(demande)

    nom_pdf = f"demande-{demande.numero_demande}.pdf"

    email_expediteur = settings.DEFAULT_FROM_EMAIL

    email_hexaquebec = getattr(
        settings,
        "HEXQUEBEC_DEMANDES_EMAIL",
        settings.DEFAULT_FROM_EMAIL,
    )

    prix = formater_prix(demande.prix_estime)

    sujet_client = (
        f"HexaQuébec — Demande reçue "
        f"{demande.numero_demande}"
    )

    message_client = f"""
Bonjour {demande.nom_complet},

Nous avons bien reçu la demande de l’entreprise {demande.nom_entreprise}.

Numéro de demande : {demande.numero_demande}
Application : {demande.nom_application}
Qualité : {demande.nom_forfait}
Prix indicatif : à partir de {prix}
Délai indicatif : {demande.delai_estime}

Votre document PDF est joint à cet email.

Notre équipe analysera votre demande avant de confirmer le prix final,
le délai de réalisation et les conditions du projet.

Merci d’avoir choisi HexaQuébec.

HexaQuébec
Développement web, applications mobiles et intelligence artificielle
""".strip()

    email_client = EmailMultiAlternatives(
        subject=sujet_client,
        body=message_client,
        from_email=email_expediteur,
        to=[demande.email],
        reply_to=[email_hexaquebec],
    )

    email_client.attach(
        nom_pdf,
        pdf,
        "application/pdf",
    )

    sujet_hexaquebec = (
        f"Nouvelle demande {demande.numero_demande} "
        f"— {demande.nom_entreprise}"
    )

    message_hexaquebec = f"""
Nouvelle demande reçue sur le site HexaQuébec.

Numéro : {demande.numero_demande}
Client : {demande.nom_complet}
Entreprise : {demande.nom_entreprise}
Email : {demande.email}
Téléphone : {demande.telephone}

Application : {demande.nom_application}
Qualité : {demande.nom_forfait}
Prix indicatif : à partir de {prix}
Délai indicatif : {demande.delai_estime}

Budget indiqué :
{demande.budget_client or "Non indiqué"}

Délai souhaité :
{demande.delai_souhaite or "Non indiqué"}

Description :
{demande.description or "Aucune description"}
""".strip()

    email_admin = EmailMultiAlternatives(
        subject=sujet_hexaquebec,
        body=message_hexaquebec,
        from_email=email_expediteur,
        to=[email_hexaquebec],
        reply_to=[demande.email],
    )

    email_admin.attach(
        nom_pdf,
        pdf,
        "application/pdf",
    )

    client_envoye = False
    hexaquebec_envoye = False

    try:
        client_envoye = bool(
            email_client.send(fail_silently=False)
        )

    except Exception:
        logger.exception(
            "Erreur email client pour %s",
            demande.numero_demande,
        )

    try:
        hexaquebec_envoye = bool(
            email_admin.send(fail_silently=False)
        )

    except Exception:
        logger.exception(
            "Erreur email HexaQuébec pour %s",
            demande.numero_demande,
        )

    demande.email_client_envoye = client_envoye
    demande.email_hexaquebec_envoye = hexaquebec_envoye

    demande.save(
        update_fields=[
            "email_client_envoye",
            "email_hexaquebec_envoye",
            "date_modification",
        ]
    )