from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from .forms import ContactForm, OrderForm
from .models import Product, Announcement, PortfolioItem
import os


import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import json
from .models import Product, Order
from .forms import OrderForm

from .models import ContactMessage
from django.utils import timezone
from openai import OpenAI
import stripe
from django.conf import settings
from .models import CartItem
from .forms import UrgenceForm






# 🔹 Charger la clé API depuis .env
load_dotenv()

# 🔹 Vérifier que la clé est bien chargée
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("La clé OPENAI_API_KEY n'est pas définie dans le fichier .env")

# 🔹 Initialiser OpenAI
openai.api_key = OPENAI_API_KEY

# 🔹 Endpoint pour le chatbot
@csrf_exempt
def chatbot_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        # Lire le message envoyé depuis le front-end
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message vide reçu."}, status=400)

        # 🔹 Appel à l’API OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es **l’assistant virtuel professionnel de HexaQuébec**. "
                        "Tu t’appelles **Assistant HexaQuébec**. "
                        "Tu réponds toujours en français, avec courtoisie et clarté. "
                        "Tu connais très bien **HexaQuébec**, le **Canada**, "
                        "l’**immigration**, la **technologie**, et le **développement web**. "
                        "Tu aides les utilisateurs à propos des **services, produits, contact** "
                        "et **informations générales** de l’entreprise."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        # Récupérer la réponse
        bot_reply = completion.choices[0].message['content'].strip()
        return JsonResponse({"reply": bot_reply})

    except Exception as e:
        print("❌ Erreur API:", e)
        return JsonResponse({"error": str(e)}, status=500)

stripe.api_key = settings.STRIPE_SECRET_KEY

def produits_list(request):
    produits = Produit.objects.filter(publie=True) # type: ignore
    return render(request, "produits.html", {"produits": produits, "stripe_pub_key": settings.STRIPE_PUBLIC_KEY})

def paiement_stripe(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id) # type: ignore
    
    # Crée une session Stripe Checkout
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "cad",
                "product_data": {
                    "name": produit.titre,
                },
                "unit_amount": int(produit.prix * 100),  # en cents
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

def home_view(request):
    annonces = Announcement.objects.filter(
        published=True,
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:5]

    products = Product.objects.filter(published=True)
    portfolio = PortfolioItem.objects.all()

    services = [
        {'title': 'Développement Web', 'description': 'Création de sites web modernes, ...', 'icon': 'fa-solid fa-laptop-code', 'image': 'images/dev.jpg'},
        {'title': 'Maintenance Informatique', 'description': 'Assistance, mise à jour ...', 'icon': 'fa-solid fa-tools', 'image': 'images/maintenance.jpg'},
    ]

    context = {
        'annonces': annonces,  # ✅ même nom que dans ton template
        'products': products,
        'portfolio': portfolio,
        'services': services,
    }
    return render(request, 'home.html', context)


def contact_view(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        email = request.POST.get("email", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        message = request.POST.get("message", "").strip()

        # Validation des champs
        if not nom or not email or not telephone or not message:
            messages.error(request, "⚠️ Tous les champs sont obligatoires. Veuillez les remplir !")
            return redirect("contact")

        # Sauvegarde dans la base de données
        ContactMessage.objects.create(
            prenom=nom.split()[0],
            nom=" ".join(nom.split()[1:]) if len(nom.split()) > 1 else "",
            email=email,
            telephone=telephone,
            message=message,
        )

        # Envoi de l’email à HexaQuébec
        try:
            send_mail(
                subject=f"Nouveau message de {nom}",
                message=f"Nom : {nom}\nEmail : {email}\nTéléphone : {telephone}\n\nMessage :\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["hexaquebec80@gmail.com"],
                fail_silently=False,
            )
        except Exception:
            messages.warning(request, "Message enregistré mais l’envoi du courriel a échoué.")

        # Message de succès
        messages.success(request, "✅ Votre message a été envoyé avec succès. Merci de nous avoir contactés !")
        return redirect("contact")

    return render(request, "contact.html")

def accueil(request):
    # Récupère toutes les annonces publiées (les plus récentes en premier)
    annonces = Announcement.objects.filter(published=True).order_by('-published_at')
    return render(request, 'home.html', {'annonces': annonces})

def portfolio_list(request):
    items = PortfolioItem.objects.all().order_by('-created_at')
    return render(request, 'portfolio.html', {'items': items})



from django.shortcuts import render

def services(request):
    return render(request, 'nos_services.html')  # résumé ou preview

def services_view(request):
    return render(request, 'services_detail.html')  # ta page détaillée actuelle


def developp_detail(request):
    return render(request, 'developp_detail.html')

def produit_detail(request, id):
    produit = get_object_or_404(Product, id=id, publie=True)
    produits = Product.objects.filter(publie=True)[:8]  # pour les produits similaires
    return render(request, "produit.html", {"produit": produit, "produits": produits})


def product_detail(request, pk):
    produit = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'produit': produit})


def annonce_detail(request, annonce_id):
    annonce = get_object_or_404(Announcement, id=annonce_id)
    return render(request, 'annonce_detail.html', {'annonce': annonce})





def home_view(request):
    annonces = Announcement.objects.filter(published=True).order_by('-published_at')
    return render(request, 'home.html', {'annonces': annonces})

# views.py
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

def test_email(request):
    try:
        send_mail(
            subject='Test HexaQuébec ✉️',
            message='Ceci est un test d’envoi de courriel depuis Django.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['hexaquebec80@gmail.com'],  # ton mail de réception
            fail_silently=False,
        )
        return HttpResponse("✅ Email envoyé avec succès ! Vérifie ta boîte Gmail.")
    except Exception as e:
        return HttpResponse(f"❌ Erreur : {e}")


def produits_list(request):
    # On récupère tous les produits publiés
    produits = Product.objects.filter(published=True)
    return render(request, "produits_list.html", {"produits": produits})







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



def passer_commande(request, id):
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








def home_view(request):
    form = UrgenceForm()
    return render(request, 'home.html', {'form': form})

def urgence_view(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = UrgenceForm(request.POST)
        if form.is_valid():
            # Ici tu peux envoyer un email ou sauvegarder les données
            # Exemple: form.save() si tu as un modèle

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)