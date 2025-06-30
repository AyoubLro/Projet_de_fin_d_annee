from django.contrib import admin
from .models import Utilisateur, Membre, Paiement, Reservation

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email')
    search_fields = ('nom', 'prenom', 'email')

@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email')
    search_fields = ('nom', 'prenom', 'email')
    filter_horizontal = ('evenements',)

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'membre', 'montant', 'statut', 'date', 'numero_facture')
    list_filter = ('statut',)
    search_fields = ('numero_facture', 'membre__nom', 'membre__prenom')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'membre', 'terrain', 'date_debut', 'date_fin', 'validee', 'annulee')
    list_filter = ('validee', 'annulee')
    search_fields = ('membre__nom', 'membre__prenom')
