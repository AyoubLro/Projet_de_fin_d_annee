from django import forms
from .models import Coach, Document

class CoachLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    motdepasse = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['fichier', 'type', 'id_coach'] 