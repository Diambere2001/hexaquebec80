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
from django.template.loader import render_to_string  
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


# ===================== HOME =====================
def home_view(request):
    annonces = Announcement.objects.filter(
        published=True,
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:5]

    products = Product.objects.filter(published=True)
    portfolio = PortfolioItem.objects.all()
    partenaires = Partenaire.objects.all()  # 🔥 On récupère les partenaires en DB

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
        'partenaires': partenaires,   # 🔥 AJOUT AU CONTEXTE
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


def paiement_success(request):
    return render(request, "success.html")


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
def passer_commande(request, id):  # correspond à <int:id> dans l'URL
    product = get_object_or_404(Product, id=id)
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            return render(request, "confirmation_commande.html", {"order": order})
    else:
        form = OrderForm()
    
    return render(request, "passer_commande.html", {"form": form, "product": product})


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

# --- Tableau de bord HexaQuébec ---
@login_required
def dashboard_hexa(request):

    # Tous les messages des clients
    messages_clients = MessageClient.objects.all().order_by('-date')

    # Tous les clients
    clients = Client.objects.all()

    return render(request, "dashboard_hexa.html", {
        "messages": messages_clients,
        "clients": clients
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
    return redirect('dashboard')  # remplace 'dashboard' par le nom réel de ta page
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
        form = OrderForm(request.POST) if 'OrderForm' in globals() else None

        if form is not None and form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            return redirect('order_receipt', order_id=order.id)
        else:
            # Création simplifiée sans formulaire
            nom = request.POST.get('nom') or 'Client'
            prenom = request.POST.get('prenom') or ''
            adresse = request.POST.get('adresse', '')
            telephone = request.POST.get('telephone', '')
            courriel = request.POST.get('courriel') or (request.user.email if request.user.is_authenticated else '')

            order = Order.objects.create(
                product=product,
                nom=nom,
                prenom=prenom,
                adresse=adresse,
                telephone=telephone,
                courriel=courriel
            )
            return redirect('order_receipt', order_id=order.id)
    else:
        form = OrderForm() if 'OrderForm' in globals() else None

    # Vérifier dernière commande de cet utilisateur pour ce produit
    last_order = None
    if request.user.is_authenticated:
        last_order = Order.objects.filter(courriel=request.user.email, product=product).last()

    barcode_base64 = None
    qrcode_base64 = None
    if last_order:
        barcode_base64 = _generate_code128_base64(last_order.code)
        qrcode_base64 = _generate_qrcode_base64(f"COMMANDE#{last_order.code} - {product.title}")

    context = {
        'product': product,
        'form': form,
        'order': last_order,
        'barcode_base64': barcode_base64,
        'qrcode_base64': qrcode_base64,
    }
    return render(request, 'order_page.html', context)


# ---------- Vue reçu de commande ----------
def order_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    prix = order.product.price

    TPS = round(prix * 0.05, 2)
    TVQ = round(prix * 0.09975, 2)
    total = round(prix + TPS + TVQ, 2)

    barcode_base64 = _generate_code128_base64(order.code)
    qrcode_base64 = _generate_qrcode_base64(f"COMMANDE#{order.code} - {order.product.title}")

    return render(request, 'order_receipt.html', {
        'order': order,
        'TPS': TPS,
        'TVQ': TVQ,
        'total': total,
        'barcode_base64': barcode_base64,
        'qrcode_base64': qrcode_base64,
    })


def download_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Génération barcode et QR code
    barcode_b64 = _generate_code128_base64(order.code)
    qr_b64 = _generate_qrcode_base64(f"COMMANDE#{order.code} - {order.product.title}")
    barcode_bytes = base64.b64decode(barcode_b64)
    qr_bytes = base64.b64decode(qr_b64)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # === LOGO ===
    try:
        logo_path = os.path.join(settings.BASE_DIR, "static/img/hexa_logo.png")
        logo = ImageReader(logo_path)
        p.drawImage(logo, 40, height - 120, width=120, height=80, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print("Erreur logo :", e)

    # === TITRE ===
    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, height - 80, "FACTURE DE COMMANDE — HEXAQUÉBEC")

    # === INFOS CLIENT ===
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 140, f"Commande : #{order.code}")
    p.drawString(40, height - 160, f"Client : {order.nom} {order.prenom}")
    p.drawString(40, height - 180, f"Courriel : {order.courriel}")
    p.drawString(40, height - 200, f"Téléphone : {order.telephone}")

    # === BARCODE + QR ===
    barcode_img = ImageReader(BytesIO(barcode_bytes))
    qr_img = ImageReader(BytesIO(qr_bytes))
    p.drawImage(barcode_img, 40, height - 300, width=300, height=70, preserveAspectRatio=True, mask='auto')
    p.drawImage(qr_img, width - 160, height - 300, width=120, height=120, preserveAspectRatio=True, mask='auto')

    # === TABLEAU PRODUITS ===
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 340, "Détails de la commande :")

    table_top = height - 360
    table_left = 40
    row_height = 25

    # Entêtes
    p.setFont("Helvetica-Bold", 11)
    p.drawString(table_left, table_top, "Produit")
    p.drawString(table_left + 250, table_top, "Quantité")
    p.drawString(table_left + 340, table_top, "Prix unitaire")
    p.drawString(table_left + 450, table_top, "Sous-total")

    # Ligne de séparation
    p.setStrokeColor(colors.grey)
    p.line(table_left, table_top - 5, width - 40, table_top - 5)

    # === PRODUIT ===
    prix_unitaire = float(order.product.price)  # <-- corrigé ici
    quantite = getattr(order, 'quantity', 1)   # si tu as un champ quantity, sinon 1
    sous_total = round(prix_unitaire * quantite, 2)

    p.setFont("Helvetica", 11)
    y = table_top - row_height
    p.drawString(table_left, y, order.product.title)
    p.drawString(table_left + 250, y, str(quantite))
    p.drawString(table_left + 340, y, f"${prix_unitaire:.2f}")
    p.drawString(table_left + 450, y, f"${sous_total:.2f}")

    # === TAXES ===
    tps = round(sous_total * 0.05, 2)
    tvq = round(sous_total * 0.09975, 2)
    total = round(sous_total + tps + tvq, 2)

    y -= row_height + 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(table_left, y, f"TPS (5%) : ${tps:.2f}")
    y -= row_height
    p.drawString(table_left, y, f"TVQ (9.975%) : ${tvq:.2f}")
    y -= row_height
    p.setFont("Helvetica-Bold", 14)
    p.drawString(table_left, y, f"Total à payer : ${total:.2f}")

    # === SIGNATURE AUTOMATIQUE ===
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(40, 60, "Document généré automatiquement par HexaQuébec — Aucun traitement manuel requis.")
    p.drawString(40, 45, "Merci pour votre confiance.")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_commande_{order.code}.pdf"'
    return response


# ---------- Vue simple pour order_product ----------

def order_product(request, product_id):
    produit = Product.objects.get(id=product_id)
    return render(request, "order_page.html", {"product": produit})


from django.http import JsonResponse

def like_produit(request, pk):
    produit = Produit.objects.get(id=pk)
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
