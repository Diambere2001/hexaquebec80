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



from django import forms
from .models import PaiementClient

class PaiementClientForm(forms.ModelForm):
    class Meta:
        model = PaiementClient
        fields = '__all__'




import base64
import binascii

from django import forms

from .models import AttestationStage


class AttestationStageForm(forms.ModelForm):

    signature_data = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
    )

    class Meta:

        model = AttestationStage

        fields = [
            "numero_stagiaire",
            "nom",
            "prenom",
            "programme",
            "date_debut",
            "date_fin",
            "lieu_delivrance",
            "responsable",
            "fonction_responsable",
            "signature_data",
        ]

        labels = {
            "numero_stagiaire": "Numéro du stagiaire",
            "nom": "Nom du stagiaire",
            "prenom": "Prénom du stagiaire",
            "programme": "Programme ou domaine du stage",
            "date_debut": "Date de début du stage",
            "date_fin": "Date de fin du stage",
            "lieu_delivrance": "Lieu de délivrance",
            "responsable": "Nom du responsable",
            "fonction_responsable": "Fonction du responsable",
        }

        widgets = {
            "numero_stagiaire": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": "Exemple : STG-12345",
                "autocomplete": "off",
            }),

            "nom": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": "Nom du stagiaire",
                "autocomplete": "off",
            }),

            "prenom": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": "Prénom du stagiaire",
                "autocomplete": "off",
            }),

            "programme": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": (
                    "Exemple : Développement web et applications"
                ),
                "autocomplete": "off",
            }),

            "date_debut": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control-pro",
                    "type": "date",
                },
            ),

            "date_fin": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control-pro",
                    "type": "date",
                },
            ),

            "lieu_delivrance": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": "Saguenay, Québec, Canada",
            }),

            "responsable": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": "Nom du responsable",
            }),

            "fonction_responsable": forms.TextInput(attrs={
                "class": "form-control-pro",
                "placeholder": "Fonction du responsable",
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")

        if (
            date_debut
            and date_fin
            and date_fin < date_debut
        ):
            self.add_error(
                "date_fin",
                (
                    "La date de fin ne peut pas être "
                    "antérieure à la date de début."
                ),
            )

        return cleaned_data

    def clean_signature_data(self):

        signature = self.cleaned_data.get(
            "signature_data",
            "",
        ).strip()

        prefixe = "data:image/png;base64,"

        if not signature:
            raise forms.ValidationError(
                "Veuillez dessiner la signature."
            )

        if not signature.startswith(prefixe):
            raise forms.ValidationError(
                "Le format de la signature est invalide."
            )

        try:

            contenu_base64 = signature.split(",", 1)[1]

            image_decodee = base64.b64decode(
                contenu_base64,
                validate=True,
            )

        except (
            ValueError,
            binascii.Error,
            IndexError,
        ):

            raise forms.ValidationError(
                "La signature électronique est invalide."
            )

        if not image_decodee.startswith(
            b"\x89PNG\r\n\x1a\n"
        ):
            raise forms.ValidationError(
                "La signature doit être une image PNG."
            )

        taille_maximale = 2 * 1024 * 1024

        if len(image_decodee) > taille_maximale:
            raise forms.ValidationError(
                "La signature est trop volumineuse."
            )

        return signature




from django import forms

from .models import DemandeApplication


class DemandeApplicationForm(forms.ModelForm):

    accepter_confidentialite = forms.BooleanField(
        required=True,
        label=(
            "J’accepte que mes renseignements soient utilisés "
            "pour traiter ma demande."
        ),
    )

    # Champ invisible contre les robots.
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = DemandeApplication

        fields = [
            "nom_complet",
            "nom_entreprise",
            "email",
            "telephone",
            "type_application",
            "qualite",
            "budget_client",
            "delai_souhaite",
            "description",
        ]

        widgets = {
            "nom_complet": forms.TextInput(
                attrs={
                    "placeholder": "Votre nom et prénom",
                    "autocomplete": "name",
                }
            ),

            "nom_entreprise": forms.TextInput(
                attrs={
                    "placeholder": "Nom de votre entreprise",
                    "autocomplete": "organization",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "exemple@entreprise.ca",
                    "autocomplete": "email",
                }
            ),

            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "+1 418 000-0000",
                    "autocomplete": "tel",
                }
            ),

            "type_application": forms.HiddenInput(),

            "qualite": forms.HiddenInput(),

            "budget_client": forms.TextInput(
                attrs={
                    "placeholder": "Exemple : 4 000 $ à 6 000 $",
                }
            ),

            "delai_souhaite": forms.TextInput(
                attrs={
                    "placeholder": "Exemple : lancement dans 3 mois",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Expliquez votre entreprise, vos clients, "
                        "vos objectifs et les fonctionnalités importantes."
                    ),
                }
            ),
        }

    def clean_website(self):
        website = self.cleaned_data.get("website")

        if website:
            raise forms.ValidationError("Soumission invalide.")

        return website

    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone", "").strip()

        chiffres = "".join(
            caractere
            for caractere in telephone
            if caractere.isdigit()
        )

        if len(chiffres) < 7:
            raise forms.ValidationError(
                "Entrez un numéro de téléphone valide."
            )

        return telephone