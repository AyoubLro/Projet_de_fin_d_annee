from django.shortcuts import render, redirect
from .forms import InscriptionForm, ConnexionForm, ProfilForm
from .models import Membre, Reservation
from django.contrib import messages
from adminclub.models import Terrain
from django.utils import timezone
from coach.models import Evenement
from datetime import datetime

# Create your views here.

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_terrains')  # Redirige vers la liste des terrains après inscription
    else:
        form = InscriptionForm()
    return render(request, 'user/inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            motdepasse = form.cleaned_data['motdepasse']
            try:
                membre = Membre.objects.get(email=email, motdepasse=motdepasse)
                messages.success(request, 'Connexion réussie !')
                # Stocker l'ID du membre dans la session
                request.session['membre_id'] = Membre.objects.get(email=email, motdepasse=motdepasse).id
                return redirect('liste_terrains')  # Redirige vers la liste des terrains après connexion
            except Membre.DoesNotExist:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = ConnexionForm()
    return render(request, 'user/login.html', {'form': form})

def liste_terrains(request):
    #id memmbre
    membre_id = request.session.get('membre_id')
    print(membre_id)
    terrains = Terrain.objects.all()
    return render(request, 'user/liste_terrains.html', {'terrains': terrains})

def reserver_terrain(request, terrain_id):
    terrain = get_object_or_404(Terrain, id=terrain_id)

    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')

        try:
            date_debut_dt = datetime.fromisoformat(date_debut)
            date_fin_dt = datetime.fromisoformat(date_fin)

            if date_debut_dt.date() != date_fin_dt.date():
                messages.error(request, "La réservation doit être sur le même jour.")
                return render(request, 'user/reserver_terrain.html', {'terrain': terrain})

        except Exception:
            messages.error(request, "Format de date invalide.")
            return render(request, 'user/reserver_terrain.html', {'terrain': terrain})

        membre_id = request.session.get('membre_id')
        if not membre_id:
            return redirect('connexion')  # ou page de connexion

        membre = get_object_or_404(Membre, id=membre_id)

        # Vérifie les conflits de réservation
        conflit = Reservation.objects.filter(
            terrain=terrain,
            date_debut__lt=date_fin_dt,
            date_fin__gt=date_debut_dt
        ).exists()

        if conflit:
            messages.error(request, "Ce créneau est déjà réservé.")
            return render(request, 'user/reserver_terrain.html', {'terrain': terrain})

        # Calcul du montant : durée en heures * prix par heure
        duree = (date_fin_dt - date_debut_dt).total_seconds() / 3600
        montant = terrain.prix * duree

        # Crée la réservation
        reservation = Reservation.objects.create(
            date_debut=date_debut_dt,
            date_fin=date_fin_dt,
            type='terrain',
            membre=membre,
            montant=montant,
            terrain=terrain
        )

        return redirect('paiement', reservation_id=reservation.id)

    return render(request, 'user/reserver_terrain.html', {'terrain': terrain})

def paiement(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    terrain = Terrain.objects.get(id=reservation.terrain_id) if hasattr(reservation, 'terrain_id') else None
    montant = terrain.prix if terrain else 0
    if request.method == 'POST':
        # Récupérer le mode de paiement depuis le formulaire
        mode_paiement = request.POST.get('mode_paiement', 'carte')
        from .models import Paiement
        statut = 'payé' if mode_paiement == 'carte' else 'en_attente'
        Paiement.objects.create(
            montant=montant,
            date=timezone.now(),
            statut=statut,
            membre=reservation.membre,
            reservation=reservation
        )
        messages.success(request, 'Paiement effectué avec succès !')
        return redirect('liste_terrains')
    return render(request, 'user/paiement.html', {'reservation': reservation, 'montant': montant, 'terrain': terrain})
from django.shortcuts import get_object_or_404
from .models import Membre  # ajuste selon l’emplacement réel de ton modèle

def profil(request):
    membre_id = request.session.get('membre_id')
    membre = get_object_or_404(Membre, pk=membre_id)  # 🔧 récupération correcte de l'objet Membre

    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=membre)
        if form.is_valid():
            membre = form.save(commit=False)
            if form.cleaned_data['motdepasse']:
                membre.motdepasse = form.cleaned_data['motdepasse']
            membre.save()
            messages.success(request, 'Informations mises à jour avec succès !')
            return redirect('liste_terrains')
    else:
        form = ProfilForm(instance=membre)

    return render(request, 'user/profil.html', {'form': form})


def liste_evenements(request):
    evenements = Evenement.objects.all()
    membre_id = request.session.get('membre_id')
    membre = get_object_or_404(Membre, id=membre_id)
    
    if request.method == 'POST':
        evenement_id = request.POST.get('evenement_id')
        evenement = Evenement.objects.get(id=evenement_id)
        membre.evenements.add(evenement)
        messages.success(request, f'Inscription à l\'événement "{evenement.titre}" réussie !')
    return render(request, 'user/liste_evenements.html', {'evenements': evenements, 'membre': membre})

def rattrapage_reservation(request, reservation_id):
    from datetime import datetime
    reservation_orig = Reservation.objects.get(id=reservation_id)
    paiement_existe = reservation_orig.paiements.filter(statut='payé').exists()
    if not (reservation_orig.annulee ):
        messages.error(request, "Vous ne pouvez pas faire de rattrapage pour cette réservation.")
        return redirect('liste_terrains')
    terrain = reservation_orig.terrain
    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        try:
            date_debut_dt = datetime.fromisoformat(date_debut)
            date_fin_dt = datetime.fromisoformat(date_fin)
            if date_debut_dt.date() != date_fin_dt.date():
                messages.error(request, "La réservation doit être sur le même jour.")
                return render(request, 'user/rattrapage_reservation.html', {'reservation_orig': reservation_orig})
        except Exception:
            messages.error(request, "Format de date invalide.")
            return render(request, 'user/rattrapage_reservation.html', {'reservation_orig': reservation_orig})
        membre = reservation_orig.membre
        nouvelle_res = Reservation.objects.create(
            date_debut=date_debut,
            date_fin=date_fin,
            type=reservation_orig.type,
            membre=membre,
            montant=0,  # Pas de paiement
            rattrapage_de=reservation_orig,
            terrain=terrain
        )
        messages.success(request, "Votre réservation de rattrapage a bien été enregistrée !")
        return redirect('liste_terrains')
    return render(request, 'user/rattrapage_reservation.html', {'reservation_orig': reservation_orig})

def mes_reservations(request):
    membre_id = request.session.get('membre_id')
    membre = get_object_or_404(Membre, id=membre_id)  # évite l'erreur si l'ID est invalide

    reservations = Reservation.objects.filter(membre=membre).order_by('-date_debut')
    return render(request, 'user/mes_reservations.html', {'reservations': reservations})


from django.contrib.auth import authenticate, login, logout
def membre_logout(request):
    # request.session.flush()
    messages.success(request, 'Déconnexion réussie !')
    return redirect('landing')

