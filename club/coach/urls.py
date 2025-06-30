from django.urls import path
from .views import coach_login, liste_membres, ajouter_membre, modifier_membre, supprimer_membre, liste_reservations, ajouter_reservation, modifier_reservation, supprimer_reservation, envoyer_document, valider_reservation, annuler_reservation, liste_documents_coach, coach_logout

urlpatterns = [
    path('login/', coach_login, name='coach_login'),
    path('membres/', liste_membres, name='liste_membres'),
    path('membres/ajouter/', ajouter_membre, name='ajouter_membre'),
    path('membres/<int:membre_id>/modifier/', modifier_membre, name='modifier_membre'),
    path('membres/<int:membre_id>/supprimer/', supprimer_membre, name='supprimer_membre'),
    path('reservations/', liste_reservations, name='liste_reservations'),
    path('reservations/ajouter/', ajouter_reservation, name='ajouter_reservation'),
    path('reservations/<int:reservation_id>/modifier/', modifier_reservation, name='modifier_reservation'),
    path('reservations/<int:reservation_id>/supprimer/', supprimer_reservation, name='supprimer_reservation'),
    path('reservations/<int:reservation_id>/valider/', valider_reservation, name='valider_reservation'),
    path('reservations/<int:reservation_id>/annuler/', annuler_reservation, name='annuler_reservation'),
    path('documents/envoyer/', envoyer_document, name='envoyer_document'),
    path('documents/', liste_documents_coach, name='liste_documents_coach'),
    path('logout/', coach_logout, name='coach_logout'),
    # Ajoute ici les routes spécifiques à coach
] 