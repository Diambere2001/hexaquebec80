from django import forms
from .models import ContactMessage, Order
from .models import ContactMessage


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







class UrgenceForm(forms.Form):
    nom = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}))
    telephone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows':4}))

