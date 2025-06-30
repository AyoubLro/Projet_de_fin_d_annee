from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Admin
from user.models import Membre, Paiement, Reservation
from coach.models import Coach, Evenement, Facture
from datetime import datetime
import pdfkit
from django.template.loader import render_to_string, get_template
from xhtml2pdf import pisa
import io
from django.views.decorators.http import require_POST

# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            admin = Admin.objects.get(email=email, password=password)
            request.session['admin_id'] = admin.id
            return redirect('admin_dashboard')
        except Admin.DoesNotExist:
            return render(request, 'adminclub/login.html', {'error': 'Email ou mot de passe incorrect.'})
    
    return render(request, 'adminclub/login.html')

def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    try:
        # Statistiques générales
        total_membres = Membre.objects.count()
        total_coachs = Coach.objects.count()
        total_factures = Paiement.objects.count()
        # Événements du jour
        aujourdhui = datetime.now().date()
        matchs_aujourdhui = Evenement.objects.filter(date=aujourdhui).count()
        
        context = {
            'total_membres': total_membres,
            'total_coachs': total_coachs,
            'matchs_aujourdhui': matchs_aujourdhui,
            'total_factures': total_factures,
        }
        
        return render(request, 'adminclub/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement du tableau de bord: {str(e)}')
        return redirect('admin_login')

def admin_evenements(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    evenements = Evenement.objects.all().order_by('-date')
    return render(request, 'adminclub/evenements.html', {'evenements': evenements})

def admin_ajouter_evenement(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        date = request.POST.get('date')
        lieu = request.POST.get('lieu')
        
        try:
            evenement = Evenement.objects.create(
                titre=titre,
                date=date,
                lieu=lieu
            )
            messages.success(request, 'Événement ajouté avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout de l\'événement: {str(e)}')
    
    return redirect('admin_evenements')

def admin_modifier_evenement(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    if request.method == 'POST':
        evenement_id = request.POST.get('evenement_id')
        titre = request.POST.get('titre')
        date = request.POST.get('date')
        lieu = request.POST.get('lieu')
        
        try:
            evenement = Evenement.objects.get(id=evenement_id)
            evenement.titre = titre
            evenement.date = date
            evenement.lieu = lieu
            evenement.save()
            messages.success(request, 'Événement modifié avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification de l\'événement: {str(e)}')
    
    return redirect('admin_evenements')

def admin_supprimer_evenement(request, evenement_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        evenement = Evenement.objects.get(id=evenement_id)
        evenement.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_evenement_details(request, evenement_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        evenement = Evenement.objects.get(id=evenement_id)
        return JsonResponse({
            'titre': evenement.titre,
            'date': evenement.date.strftime('%Y-%m-%d'),
            'lieu': evenement.lieu
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_participants(request, evenement_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    evenement = get_object_or_404(Evenement, id=evenement_id)
    participants = [{
        'id': p.id,
        'nom': p.nom,
        'prenom': p.prenom
    } for p in evenement.participants.all()]
    
    return JsonResponse({'participants': participants})


def retirer_participant(request, evenement_id, participant_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        evenement = get_object_or_404(Evenement, id=evenement_id)
        participant = get_object_or_404(Membre, id=participant_id)
        evenement.participants.remove(participant)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def admin_coachs(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    search_query = request.GET.get('search', '')
    if search_query:
        coachs = Coach.objects.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(email__icontains=search_query)
        ).order_by('nom', 'prenom')
    else:
        coachs = Coach.objects.all().order_by('nom', 'prenom')
    
    return render(request, 'adminclub/coachs.html', {'coachs': coachs})

def admin_ajouter_coach(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        motdepasse = request.POST.get('motdepasse')
        
        try:
            # Vérifier si l'email existe déjà
            if Coach.objects.filter(email=email).exists():
                messages.error(request, 'Cet email est déjà utilisé.')
                return redirect('admin_coachs')
            
            coach = Coach.objects.create(
                nom=nom,
                prenom=prenom,
                email=email,
                motdepasse=motdepasse
            )
            messages.success(request, 'Coach ajouté avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout du coach: {str(e)}')
    
    return redirect('admin_coachs')

def admin_modifier_coach(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    if request.method == 'POST':
        coach_id = request.POST.get('coach_id')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        motdepasse = request.POST.get('motdepasse')
        
        try:
            coach = Coach.objects.get(id=coach_id)
            
            # Vérifier si l'email existe déjà pour un autre coach
            if Coach.objects.filter(email=email).exclude(id=coach_id).exists():
                messages.error(request, 'Cet email est déjà utilisé par un autre coach.')
                return redirect('admin_coachs')
            
            coach.nom = nom
            coach.prenom = prenom
            coach.email = email
            if motdepasse:  # Ne changer le mot de passe que s'il est fourni
                coach.motdepasse = motdepasse
            coach.save()
            
            messages.success(request, 'Coach modifié avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification du coach: {str(e)}')
    
    return redirect('admin_coachs')

def admin_supprimer_coach(request, coach_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        coach = Coach.objects.get(id=coach_id)
        coach.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_coach_details(request, coach_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        coach = Coach.objects.get(id=coach_id)
        return JsonResponse({
            'nom': coach.nom,
            'prenom': coach.prenom,
            'email': coach.email
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def admin_factures(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    # Récupérer les filtres
    search_query = request.GET.get('search', '')
    statut = request.GET.get('statut', '')
    date = request.GET.get('date', '')
    
    # Filtrer les factures
    factures = Facture.objects.all()
    
    if search_query:
        factures = factures.filter(
            Q(numero__icontains=search_query) |
            Q(membre__nom__icontains=search_query) |
            Q(membre__prenom__icontains=search_query) |
            Q(evenement__titre__icontains=search_query)
        )
    
    if statut:
        factures = factures.filter(statut=statut)
    
    if date:
        factures = factures.filter(date_emission__date=date)
    
    factures = factures.order_by('-date_emission')
    
    # Récupérer les membres et événements pour le formulaire
    membres = Membre.objects.all().order_by('nom', 'prenom')
    evenements = Evenement.objects.all().order_by('-date')
    
    context = {
        'factures': factures,
        'membres': membres,
        'evenements': evenements
    }
    
    return render(request, 'adminclub/factures.html', context)

def admin_generer_facture(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    if request.method == 'POST':
        membre_id = request.POST.get('membre_id')
        evenement_id = request.POST.get('evenement_id')
        montant = request.POST.get('montant')
        
        try:
            # Validation du montant
            montant = float(montant)
            if montant <= 0:
                messages.error(request, 'Le montant doit être supérieur à 0.')
                return redirect('admin_factures')
            
            membre = Membre.objects.get(id=membre_id)
            evenement = Evenement.objects.get(id=evenement_id)
            
            # Vérifier si une facture existe déjà pour ce membre et cet événement
            if Facture.objects.filter(membre=membre, evenement=evenement).exists():
                messages.error(request, 'Une facture existe déjà pour ce membre et cet événement.')
                return redirect('admin_factures')
            
            facture = Facture.objects.create(
                membre=membre,
                evenement=evenement,
                montant=montant
            )
            
            messages.success(request, f'Facture {facture.numero} générée avec succès.')
        except ValueError:
            messages.error(request, 'Le montant doit être un nombre valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération de la facture: {str(e)}')
    
    return redirect('admin_factures')

def telecharger_facture(request, facture_id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    try:
        facture = get_object_or_404(Facture, id=facture_id)
        
        # Générer le HTML de la facture
        html = render_to_string('adminclub/facture_pdf.html', {
            'facture': facture,
            'club': {
                'nom': 'SportClub',
                'adresse': '123 Rue du Sport',
                'ville': 'Ville Sportive',
                'code_postal': '75000',
                'telephone': '01 23 45 67 89',
                'email': 'contact@sportclub.com'
            }
        })
        
        try:
            # Convertir le HTML en PDF
            pdf = pdfkit.from_string(html, False)
            
            # Créer la réponse HTTP avec le PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
            
            return response
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
            return redirect('admin_factures')
            
    except Exception as e:
        messages.error(request, f'Erreur lors de la récupération de la facture: {str(e)}')
        return redirect('admin_factures')

def marquer_facture_payee(request, facture_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        facture = Facture.objects.get(id=facture_id)
        facture.statut = 'payee'
        facture.date_paiement = timezone.now()
        facture.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def annuler_facture(request, facture_id):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        facture = Facture.objects.get(id=facture_id)
        facture.statut = 'annulee'
        facture.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

WKHTMLTOPDF_PATH = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'

def telecharger_facture_reservation(request, paiement_id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    try:
        paiement = get_object_or_404(Paiement, id=paiement_id)
        if paiement.statut != 'payé':
            messages.error(request, 'Ce paiement n\'est pas encore payé.')
            return redirect('admin_factures_reservations')
        template_path = 'adminclub/facture_reservation.html'
        context = {
            'paiement': paiement,
            'club': {
                'nom': 'SportClub',
                'adresse': '140 lot adarissa Sidi Maarouf',
                'ville': 'casablanca',
                'code_postal': '20500',
                'telephone': '06 06 87 30 74 ',
                'email': 'contact@sportclub.com'
            }
        }
        template = get_template(template_path)
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{paiement.numero_facture or paiement.id}.pdf"'
        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=result)
        if pisa_status.err:
            return HttpResponse('Erreur lors de la génération du PDF', status=500)
        response.write(result.getvalue())
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de la récupération du paiement: {str(e)}')
        return redirect('admin_factures_reservations')

def admin_factures_reservations(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    try:
        # Récupérer tous les paiements avec leurs relations
        paiements = Paiement.objects.select_related(
            'membre',
            'reservation',
            'reservation__terrain'
        ).order_by('-date')
        
        context = {
            'paiements': paiements
        }
        
        return render(request, 'adminclub/factures_reservations.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement des factures: {str(e)}')
        return redirect('admin_dashboard')

@require_POST
def valider_paiement(request, paiement_id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    from user.models import Paiement
    paiement = get_object_or_404(Paiement, id=paiement_id)
    if paiement.statut == 'en_attente':
        paiement.statut = 'payé'
        paiement.save()
        messages.success(request, 'Paiement validé avec succès.')
    else:
        messages.warning(request, 'Ce paiement n\'est pas en attente.')
    return redirect('admin_factures_reservations')

from adminclub.models import Terrain

def admin_terrains(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    terrains = Terrain.objects.all()
    return render(request, 'adminclub/terrains.html', {'terrains': terrains})

def ajouter_terrain(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    if request.method == 'POST':
        nom = request.POST.get('nom')
        image = request.FILES.get('image')
        disponibilite = request.POST.get('disponibilite')
        prix = request.POST.get('prix')
        try:
            terrain = Terrain.objects.create(
                nom=nom,
                image=image,
                disponibilite=disponibilite,
                prix=prix
            )
            messages.success(request, 'Terrain ajouté avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout du terrain: {str(e)}')
    return redirect('admin_terrains')
    
    
def supprimer_terrain(request, terrain_id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    terrain = get_object_or_404(Terrain, id=terrain_id)
    terrain.delete()
    messages.success(request, 'Terrain supprimé avec succès.')
    return redirect('admin_terrains')

def modifier_terrain(request, terrain_id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    terrain = get_object_or_404(Terrain, id=terrain_id)
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.POST.get('nom')
            prix = request.POST.get('prix')
            disponibilite = request.POST.get('disponibilite')
            image = request.FILES.get('image')
            
            # Validation des données
            if not nom:
                messages.error(request, 'Le nom du terrain est obligatoire.')
                return redirect('admin_terrains')
            
            if not prix:
                messages.error(request, 'Le prix du terrain est obligatoire.')
                return redirect('admin_terrains')
            
            try:
                prix = float(prix)
                if prix <= 0:
                    messages.error(request, 'Le prix doit être supérieur à 0.')
                    return redirect('admin_terrains')
            except ValueError:
                messages.error(request, 'Le prix doit être un nombre valide.')
                return redirect('admin_terrains')
            
            # Mise à jour du terrain
            terrain.nom = nom
            terrain.prix = prix
            terrain.disponibilite = disponibilite == 'True'
            
            # Mise à jour de l'image seulement si une nouvelle image est fournie
            if image:
                terrain.image = image
            
            terrain.save()
            messages.success(request, f'Le terrain "{nom}" a été modifié avec succès.')
            
        except Exception as e:
            messages.error(request, f'Une erreur est survenue lors de la modification du terrain: {str(e)}')
    
    return redirect('admin_terrains')

from coach.models import Document
def liste_documents(request):
    documents = Document.objects.all()
    return render(request, 'adminclub/liste_documents.html', {'documents': documents})

def admin_logout(request):
    request.session.clear()
    return redirect('landing')