from django.urls import path
from .views import inscription, connexion,membre_logout, liste_terrains, reserver_terrain, paiement, profil, liste_evenements, rattrapage_reservation, mes_reservations

urlpatterns = [
    path('inscription/', inscription, name='inscription'),
    path('login/', connexion, name='login'),
    path('terrains/', liste_terrains, name='liste_terrains'),
    path('terrains/<int:terrain_id>/reserver/', reserver_terrain, name='reserver_terrain'),
    path('paiement/<int:reservation_id>/', paiement, name='paiement'),
    path('profil/', profil, name='profil'),
    path('evenements/', liste_evenements, name='liste_evenements'),
    path('rattrapage/<int:reservation_id>/', rattrapage_reservation, name='rattrapage_reservation'),
    path('mes-reservations/', mes_reservations, name='mes_reservations'),
    path('logout/', membre_logout, name='membre_logout'),
    
] 