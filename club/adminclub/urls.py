from django.urls import path
from . import views

urlpatterns = [
    # Ajoute ici les routes spécifiques à adminclub
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('evenements/', views.admin_evenements, name='admin_evenements'),
    path('evenements/ajouter/', views.admin_ajouter_evenement, name='admin_ajouter_evenement'),
    path('evenements/modifier/', views.admin_modifier_evenement, name='admin_modifier_evenement'),
    path('evenement/<int:evenement_id>/', views.get_evenement_details, name='get_evenement_details'),
    path('evenement/<int:evenement_id>/supprimer/', views.admin_supprimer_evenement, name='admin_supprimer_evenement'),
    path('coachs/', views.admin_coachs, name='admin_coachs'),
    path('coachs/ajouter/', views.admin_ajouter_coach, name='admin_ajouter_coach'),
    path('coachs/modifier/', views.admin_modifier_coach, name='admin_modifier_coach'),
    path('coach/<int:coach_id>/', views.get_coach_details, name='get_coach_details'),
    path('coach/<int:coach_id>/supprimer/', views.admin_supprimer_coach, name='admin_supprimer_coach'),
    path('factures/', views.admin_factures, name='admin_factures'),
    path('factures/generer/', views.admin_generer_facture, name='admin_generer_facture'),
    path('facture/<int:facture_id>/telecharger/', views.telecharger_facture, name='telecharger_facture'),
    path('facture/<int:facture_id>/marquer-payee/', views.marquer_facture_payee, name='marquer_facture_payee'),
    path('facture/<int:facture_id>/annuler/', views.annuler_facture, name='annuler_facture'),
    path('factures-reservations/', views.admin_factures_reservations, name='admin_factures_reservations'),
    path('paiement/<int:paiement_id>/facture/', views.telecharger_facture_reservation, name='telecharger_facture_reservation'),
    path('paiement/<int:paiement_id>/valider/', views.valider_paiement, name='valider_paiement'),
    path('terrains/', views.admin_terrains, name='admin_terrains'),
    path('terrains/ajouter/', views.ajouter_terrain, name='ajouter_terrain'),
    path('terrains/modifier/<int:terrain_id>/', views.modifier_terrain, name='modifier_terrain'),
    path('terrains/supprimer/<int:terrain_id>/', views.supprimer_terrain, name='supprimer_terrain'),
    path('documents/', views.liste_documents, name='liste_documents'),
    path('logout/', views.admin_logout, name='admin_logout'),

] 