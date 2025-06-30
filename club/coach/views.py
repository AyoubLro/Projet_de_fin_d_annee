from django.shortcuts import render, redirect, get_object_or_404
from .forms import CoachLoginForm, DocumentForm
from .models import Coach
from django.contrib import messages
from user.models import Membre, Reservation
from user.forms import InscriptionForm, ProfilForm
from django import forms
from collections import defaultdict

# Create your views here.

def coach_login(request):
    if request.method == 'POST':
        form = CoachLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            motdepasse = form.cleaned_data['motdepasse']
            try:
                coach = Coach.objects.get(email=email, motdepasse=motdepasse)
                # Stocker l'ID du coach dans la session
                request.session['coach_id'] = coach.id
                messages.success(request, 'Connexion coach réussie !')
                return redirect('liste_membres')
            except Coach.DoesNotExist:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = CoachLoginForm()
    return render(request, 'coach/login.html', {'form': form})


def liste_membres(request):
    # Vérifier si le coach est connecté
    coach_id = request.session.get('coach_id')
    print(coach_id)
    
    query = request.GET.get('q', '')
    if query:
        membres = Membre.objects.filter(nom__icontains=query) | Membre.objects.filter(prenom__icontains=query)
    else:
        membres = Membre.objects.all()
    return render(request, 'coach/liste_membres.html', {'membres': membres, 'query': query})

def ajouter_membre(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_membres')
    else:
        form = InscriptionForm()
    return render(request, 'coach/ajouter_membre.html', {'form': form})

def modifier_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            return redirect('liste_membres')
    else:
        form = ProfilForm(instance=membre)
    return render(request, 'coach/modifier_membre.html', {'form': form, 'membre': membre})

def supprimer_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    membre.delete()
    return redirect('liste_membres')

def liste_reservations(request):
    reservations = Reservation.objects.all().order_by('date_debut')
    # Grouper par jour
    reservations_par_jour = defaultdict(list)
    for res in reservations:
        jour = res.date_debut.date()
        reservations_par_jour[jour].append(res)
    reservations_groupes = [(jour, res_list) for jour, res_list in reservations_par_jour.items()]
    reservations_groupes.sort()  # Tri par date
    return render(request, 'coach/liste_reservations.html', {
        'reservations_groupes': reservations_groupes,
    })

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['membre', 'date_debut', 'date_fin', 'type', 'montant']

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        if date_debut and date_fin:
            if date_debut.date() != date_fin.date():
                raise forms.ValidationError("La réservation doit être sur le même jour.")
        return cleaned_data

def ajouter_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_reservations')
    else:
        form = ReservationForm()
    return render(request, 'coach/ajouter_reservation.html', {'form': form})

def modifier_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('liste_reservations')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'coach/modifier_reservation.html', {'form': form, 'reservation': reservation})

def supprimer_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.delete()
    return redirect('liste_reservations')

def envoyer_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            # Récupérer le coach connecté depuis la session
            coach_id = request.session.get('coach_id')
            if coach_id:
                print('coach_id dans la session:', coach_id)
                print('document.id_coach_id avant save:', document.id_coach_id)
                document.id_coach_id = coach_id
            document.save()
            messages.success(request, 'Document envoyé avec succès !')
            return redirect('liste_membres')
    else:
        form = DocumentForm()
    return render(request, 'coach/envoyer_document.html', {'form': form})

def valider_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.validee = True
    reservation.save()
    messages.success(request, 'Réservation validée avec succès !')
    return redirect('liste_reservations')

def annuler_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.annulee = True
    reservation.save()
    messages.success(request, 'Réservation annulée avec succès !')
    return redirect('liste_reservations')

from .models import Document
def liste_documents_coach(request):
    coach_id = request.session.get('coach_id')
    print(coach_id)
    documents = Document.objects.all()
    return render(request, 'coach/liste_documents.html', {'documents': documents})

from django.contrib.auth import authenticate, login, logout
def coach_logout(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie !')
    return redirect('landing')