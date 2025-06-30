from django import forms
from .models import Membre

class InscriptionForm(forms.ModelForm):
    motdepasse = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Membre
        fields = ['nom', 'prenom', 'email', 'motdepasse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ConnexionForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    motdepasse = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Mot de passe')

class ProfilForm(forms.ModelForm):
    motdepasse = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = Membre
        fields = ['nom', 'prenom', 'email', 'motdepasse'] 