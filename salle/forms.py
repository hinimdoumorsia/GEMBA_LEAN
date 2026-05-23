from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ChaiseForm(forms.ModelForm):
    class Meta:
        model = Chaise
        fields = ['code_unique', 'salle', 'etat', 'description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'code_unique': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CHAISE_001'}),
            'salle': forms.Select(attrs={'class': 'form-control'}),
            'etat': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class OrdinateurForm(forms.ModelForm):
    class Meta:
        model = Ordinateur
        fields = ['code_unique', 'salle', 'etat', 'description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'code_unique': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PC_001'}),
            'salle': forms.Select(attrs={'class': 'form-control'}),
            'etat': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RapportForm(forms.ModelForm):
    class Meta:
        model = RapportSalle
        fields = ['salle', 'photo', 'commentaire', 'ordre_general']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Décrivez l\'état général de la salle...'}),
            'salle': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'ordre_general': forms.Select(attrs={'class': 'form-control'}),
        }

class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ['type_probleme', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Décrivez précisément le problème...'}),
            'type_probleme': forms.Select(attrs={'class': 'form-control'}),
        }

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['salle', 'professeur', 'niveau', 'semestre', 'date_seance', 'commentaire']  # SUPPRIMÉ 'filiere'
        widgets = {
            'date_seance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salle': forms.Select(attrs={'class': 'form-control'}),
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Optionnel'}),
        }

class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['matricule', 'nom', 'prenom', 'niveau', 'email', 'telephone', 'chaise_associee', 'pc_associe']  # SUPPRIMÉ 'filiere'
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ENSAM001'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@ensam.ma'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '06XXXXXXXX'}),
            'chaise_associee': forms.Select(attrs={'class': 'form-control'}),
            'pc_associe': forms.Select(attrs={'class': 'form-control'}),
        }

class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['nom', 'capacite', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salle 101'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }