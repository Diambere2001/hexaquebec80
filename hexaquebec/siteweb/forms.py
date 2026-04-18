from django import forms
from .models import ContactMessage, Order
from .models import ContactMessage
from .models import Client
from .models import Message
from .models import MessageClient, RendezVous, Partenaire
from .models import Product, CommentPro


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["prenom", "nom", "telephone", "adresse", "email", "message"]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }


# forms.py
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["nom", "prenom", "adresse", "telephone", "courriel"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre nom"}),
            "prenom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre prénom"}),
            "adresse": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Votre adresse complète"}),
            "telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre numéro de téléphone"}),
            "courriel": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Votre courriel"}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['prenom', 'nom', 'email', 'telephone', 'adresse', 'message']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:
            raise forms.ValidationError("Veuillez entrer une adresse courriel valide.")
        return email


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'quality', 'stock', 'image', 'published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quality': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }





class UrgenceForm(forms.Form):
    nom = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}))
    telephone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows':4}))





class ClientRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Client
        fields = ['entreprise', 'contact', 'adresse']

    email = forms.EmailField()
    username = forms.CharField(label="Nom d'utilisateur")

class ClientLoginForm(forms.Form):
    numero_client = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class MessageClientForm(forms.ModelForm):
    # 📷 Image (optionnelle)
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label="📷 Joindre une image"
    )

    # 📎 Fichier (optionnel)
    fichier = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        }),
        label="📎 Joindre un fichier"
    )

    class Meta:
        model = MessageClient
        fields = ['message', 'image', 'fichier']  # ✅ IMPORTANT

        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '✍️ Écris ton message ici...',
                'rows': 3,
                'style': 'resize:none;'
            }),
        }

        labels = {
            'message': 'Message'
        }


class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ["date", "heure", "service"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "heure": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "service": forms.Select(attrs={"class": "form-control"}),
        }
class PartenaireForm(forms.ModelForm):
    class Meta:
        model = Partenaire
        fields = ['nom_entreprise', 'telephone', 'activite', 'logo']

        widgets = {
            'nom_entreprise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom de l'entreprise"
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Téléphone de contact"
            }),
            'activite': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "Décrivez l'activité de votre entreprise...",
                'rows': 3
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

        labels = {
            'logo': "Logo de l'entreprise (optionnel)"
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = MessageClient
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3})
        }


from .models import MessageContact

class AdminSendMailForm(forms.Form):
    email = forms.EmailField(label="Envoyer à")
    sujet = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

class ContactClientForm(forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'sujet', 'message']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinataire_email', 'objet', 'contenu', 'fichier']  # ajouter 'fichier'

        widgets = {
            'destinataire_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email du destinataire'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet du message'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre message…'
            }),
            'fichier': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class CommentProForm(forms.ModelForm):
    class Meta:
        model = CommentPro
        fields = ['commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Écrire un commentaire...'
            })
        }


from django import forms
from .models import ProfilStagiaire

class ProfilStagiaireForm(forms.ModelForm):
    class Meta:
        model = ProfilStagiaire
        fields = ['photo']

