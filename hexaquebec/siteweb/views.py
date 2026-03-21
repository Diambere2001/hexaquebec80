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





from .models import (
    Product,
    Announcement,
    PortfolioItem,
    ContactMessage,
    CartItem,
    Commentaire,
)
from .forms import ContactForm, OrderForm, UrgenceForm
from django.contrib.auth import authenticate, login, logout
from .models import Client
from .forms import ClientRegisterForm, ClientLoginForm, MessageClientForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Client, MessageClient, RendezVous, Partenaire
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
    return render(request, 'siteweb/annonces.html', {'annonces': annonces})


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


def paiement_success(request, order_id):

    order = Order.objects.get(id=order_id)

    order.paid = True
    order.save()

    email = EmailMessage(

        "Confirmation de commande HexaQuébec",

        f"""
Merci pour votre commande.

Numéro : {order.code}

Produit : {order.product.title}

Total payé : {order.total}$

Votre facture est jointe.
""",

        "contact@hexaquebec.com",

        [order.courriel],

    )

    invoice = generate_invoice(order)

    email.attach(f"facture_{order.code}.pdf", invoice.content, "application/pdf")

    email.send()

    return render(request, "success.html", {"order": order})


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
    
def paiement_success(request):

    product_id = request.GET.get("product_id")

    product = Product.objects.get(id=product_id)

    price = Decimal(product.price)

    tps = price * Decimal("0.05")
    tvq = price * Decimal("0.09975")

    total = price + tps + tvq

    order = Order.objects.create(
        user=request.user,
        product=product,
        price=price,
        tps=tps,
        tvq=tvq,
        total=total
    )

    pdf = generate_invoice(order)

    email = EmailMessage(
        "Facture - HexaQuebec",
        f"""
Merci pour votre commande.

Produit : {product.title}

Numéro de commande : {order.order_number}

TOTAL payé : {total} CAD

Votre facture est attachée à cet email.

HexaQuebec
""",
        "noreply@hexaquebec.com",
        [request.user.email],
    )

    email.attach(f"facture_{order.order_number}.pdf", pdf.read(), "application/pdf")

    email.send()

    return render(request, "paiement_success.html", {"order": order})



def generate_invoice(order):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(buffer, pagesize=letter) # type: ignore

    styles = getSampleStyleSheet() # type: ignore
    elements = []

    logo = "static/logo.png"
    elements.append(Image(logo, width=120, height=60))

    elements.append(pager(1,20))

    elements.append(Paragraph("Facture - HexaQuebec", styles['Title'])) # type: ignore

    elements.append(Spacer(1,20)) # type: ignore

    elements.append(Paragraph(f"Commande #: {order.order_number}", styles['Normal'])) # type: ignore
    elements.append(Paragraph(f"Produit: {order.product.title}", styles['Normal'])) # type: ignore

    elements.append(Spacer(1,20)) # type: ignore

    elements.append(Paragraph(f"Prix: {order.price} CAD", styles['Normal'])) # type: ignore
    elements.append(Paragraph(f"TPS (5%): {order.tps} CAD", styles['Normal'])) # type: ignore
    elements.append(Paragraph(f"TVQ (9.975%): {order.tvq} CAD", styles['Normal'])) # type: ignore
    elements.append(Paragraph(f"TOTAL: {order.total} CAD", styles['Heading2'])) # type: ignore

    pdf.build(elements)

    buffer.seek(0)

    return buffer



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
    client = get_object_or_404(Client, user=request.user)

    messages_recu = MessageClient.objects.filter(client=client).order_by('-date')

    message_form = MessageClientForm()
    rdv_form = RendezVousForm()
    partenaire_form = PartenaireForm()

    # Récupérer tous les partenaires (ou filtrer selon ton modèle)
    partenaires = Partenaire.objects.all()

    # Vérifier si le client est déjà partenaire
    client_est_partenaire = partenaires.filter(id=client.id).exists()

    if request.method == "POST":

        if "send_message" in request.POST:
            message_form = MessageClientForm(request.POST)
            if message_form.is_valid():
                msg = message_form.save(commit=False)
                msg.client = client
                msg.expediteur = request.user
                msg.save()
                messages.success(request, "📩 Votre message a été envoyé.")
                return redirect("client_profile")

        elif "send_rdv" in request.POST:
            rdv_form = RendezVousForm(request.POST)
            if rdv_form.is_valid():
                rdv = rdv_form.save(commit=False)
                rdv.client = client
                rdv.save()
                messages.success(request, "📅 Votre demande de rendez-vous a été envoyée.")
                return redirect("client_profile")

        elif "send_partenaire" in request.POST:
            partenaire_form = PartenaireForm(request.POST)
            if partenaire_form.is_valid():
                partenaire = partenaire_form.save(commit=False)
                partenaire.client = client
                partenaire.save()
                messages.success(request, "🤝 Votre demande partenaire a été envoyée.")
                return redirect("client_profile")

    context = {
        "client": client,
        "messages_recu": messages_recu,
        "message_form": message_form,
        "rdv_form": rdv_form,
        "partenaire_form": partenaire_form,
        "partenaires": partenaires,
        "client_est_partenaire": client_est_partenaire,  # pour template
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

@login_required
def dashboard_hexa(request):

    # Tous les messages des clients
    messages_clients = MessageClient.objects.all().order_by('-date')

    # Tous les clients
    clients = Client.objects.all()

    # Toutes les factures
    factures = Facture.objects.all().order_by('date')

    # Toutes les commandes
    orders = Order.objects.select_related('product').all().order_by('-id')

    # Données pour Chart.js
    factures_labels = [f.date.strftime('%b %Y') for f in factures]
    factures_data = [float(f.prix) for f in factures]

    return render(request, "dashboard_hexa.html", {
        "messages": messages_clients,
        "clients": clients,
        "factures": factures,
        "orders": orders,   # 🔥 important pour ton tableau commandes

        "factures_labels": json.dumps(factures_labels),
        "factures_data": json.dumps(factures_data),
    })

def repondre_message(request, message_id):
    # Récupère le message
    message_obj = get_object_or_404(MessageClient, id=message_id)

    if request.method == "POST":
        reponse = request.POST.get('reponse', '').strip()
        if reponse:
            message_obj.reponse = reponse
            from django.utils import timezone
            message_obj.date_reponse = timezone.now()
            message_obj.save()
            messages.success(request, f"Réponse envoyée à {message_obj.client.user.username} !")
        else:
            messages.error(request, "Veuillez écrire une réponse avant d'envoyer.")

    # Redirige vers le dashboard
    return redirect('dashboard')
    
    
     # remplace 'dashboard' par le nom réel de ta page
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


def creer_facture(request):

    if request.method == "POST":

        vendeur = request.POST.get("vendeur")
        acheteur = request.POST.get("acheteur")
        produit = request.POST.get("produit")
        prix = request.POST.get("prix")
        date = request.POST.get("date")
        signature = request.POST.get("signature")

        # compter les factures existantes
        total = Facture.objects.count() + 1

        numero_facture = f"HEX-{total}"

        facture = Facture.objects.create(
            numero=numero_facture,
            vendeur_nom=vendeur,
            acheteur_nom=acheteur,
            produit=produit,
            prix=prix,
            date=date,
            signature_vendeur=signature
        )

        return redirect("facture_detail", id=facture.id)

    return render(request, "facture_form.html")




import qrcode
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from .models import Facture
from reportlab.lib.utils import ImageReader
import base64
from io import BytesIO

def fact_pdf(request, facture_id):

    facture = Facture.objects.get(id=facture_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="facture_{facture.numero}.pdf"'

    # ton code PDF ici...



    p = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # ======================
    # HEADER
    # ======================

    p.setFillColor(HexColor("#2c3e50"))
    p.setFont("Helvetica-Bold", 24)
    p.drawString(40, height-50, "HexaQuebec")

    p.setFont("Helvetica-Bold", 18)
    p.drawRightString(width-40, height-50, f"FACTURE #{facture.numero}")

    p.line(40, height-60, width-40, height-60)

    # ======================
    # INFO ENTREPRISE
    # ======================

    p.setFont("Helvetica", 10)
    p.drawString(40, height-90, "HexaQuebec")
    p.drawString(40, height-105, "Entreprise de développement Web et Mobile")
    p.drawString(40, height-120, "Vente de services informatiques")
    p.drawString(40, height-135, "Maintenance et réparation d'ordinateurs")
    p.drawString(40, height-150, "Saguenay, Québec, Canada")

    # ======================
    # DESCRIPTION
    # ======================

    p.drawString(40, height-180, "Cette facture est établie lorsque l'entreprise achète un ordinateur")
    p.drawString(40, height-195, "ou tout autre service informatique auprès d'une personne.")
    p.drawString(40, height-210, "Avant toute revente, chaque équipement est soigneusement vérifié")
    p.drawString(40, height-225, "afin de garantir la qualité et d'éviter tout matériel défectueux.")
    p.drawString(40, height-240, "Tous nos services sont garantis et les taxes applicables")
    p.drawString(40, height-255, "sont incluses dans le montant total.")

    # ======================
    # CLIENT / VENDEUR
    # ======================

    client_y = height - 300

    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, client_y, "Facturé à :")

    p.setFont("Helvetica", 11)
    p.drawString(40, client_y-15, facture.acheteur_nom)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(width/2, client_y, "Vendeur :")

    p.setFont("Helvetica", 11)
    p.drawString(width/2, client_y-15, facture.vendeur_nom)

    p.drawString(width/2, client_y-35, f"Date : {facture.date}")

    # ======================
    # TABLEAU FACTURE
    # ======================

    table_top = height - 350

    p.setFillColor(HexColor("#2c3e50"))
    p.rect(40, table_top, width-80, 25, fill=1)

    p.setFillColor("white")
    p.setFont("Helvetica-Bold", 11)

    p.drawString(50, table_top+7, "Description")
    p.drawString(300, table_top+7, "Quantité")
    p.drawString(380, table_top+7, "Prix")
    p.drawString(460, table_top+7, "Total")

    # ligne produit

    p.setFillColor("black")
    p.setFont("Helvetica", 11)

    y = table_top - 25

    p.drawString(50, y, facture.produit)
    p.drawString(300, y, "1")
    p.drawString(380, y, f"{facture.prix} $")
    p.drawString(460, y, f"{facture.prix} $")

    p.line(40, y-10, width-40, y-10)

    # ======================
    # TOTAL
    # ======================

    total_y = y - 60

    p.setFont("Helvetica", 12)
    p.drawRightString(width-150, total_y, "Sous-total :")
    p.drawRightString(width-40, total_y, f"{facture.prix} $")

    p.drawRightString(width-150, total_y-20, "Taxes :")
    p.drawRightString(width-40, total_y-20, "0 $")

    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width-150, total_y-45, "TOTAL :")
    p.drawRightString(width-40, total_y-45, f"{facture.prix} $")

    # ======================
    # SIGNATURE
    # ======================

    p.setFont("Helvetica", 11)
    p.drawString(40, total_y - 90, "Signature :")

    signature = facture.signature_vendeur

    if signature and "base64" in signature:

        format, imgstr = signature.split(';base64,')
        img_data = base64.b64decode(imgstr)

        image = ImageReader(BytesIO(img_data))

        p.drawImage(
            image,
            120, total_y - 110,
            width=150,
            height=50,
            mask='auto'
        )

    # ======================
    # FOOTER
    # ======================

    p.line(40, 120, width-40, 120)

    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, 100, "Facture originale - HexaQuebec")

    p.setFont("Helvetica", 9)

    p.drawString(40, 80, "HexaQuebec - Solutions numériques professionnelles")
    p.drawString(40, 65, "Développement Web | Développement Mobile | Services informatiques")
    p.drawString(40, 50, "Maintenance et réparation d’ordinateurs")

    p.showPage()
    p.save()

    return response


def facture_detail(request, id):
    facture = get_object_or_404(Facture, id=id)
    
    context = {
        "facture": facture
    }
    
    return render(request, "facture_detail.html", context)


def facture_list(request):
    # Récupérer toutes les factures ou celles liées à l'utilisateur
    factures = Facture.objects.all()
    return render(request, "facture_list.html", {"factures": factures})


def facture_edit(request, id):

    facture = Facture.objects.get(id=id)

    if request.method == "POST":
        facture.vendeur_nom = request.POST.get("vendeur_nom")
        facture.acheteur_nom = request.POST.get("acheteur_nom")
        facture.produit = request.POST.get("produit")
        facture.prix = request.POST.get("prix")
        facture.date = request.POST.get("date")

        facture.save()

        return redirect("facture_list")

    return render(request,"facture_edit.html",{"facture":facture})


@login_required
def facture_delete(request, facture_id):
    # Vérifie si la facture existe
    try:
        facture = Facture.objects.get(id=facture_id)
    except Facture.DoesNotExist:
        messages.error(request, "Cette facture n'existe pas.")
        return redirect('facture_list')  # ou dashboard

    if request.method == "POST":
        facture.delete()
        messages.success(request, "Facture supprimée avec succès !")
    return redirect('facture_list')  # ou dashboard



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