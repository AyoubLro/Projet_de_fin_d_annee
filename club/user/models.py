from django.db import models
from adminclub.models import Terrain
from datetime import datetime

# Create your models here.

class Utilisateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    motdepasse = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Membre(Utilisateur):
    evenements = models.ManyToManyField('coach.Evenement', blank=True, related_name='membres_inscrits')
    # Hérite de Utilisateur
    def creer_compte(self):
        pass
    def reserver_terrain(self):
        pass
    def inscription_evenement(self):
        pass
    def paiement(self):
        pass

class Paiement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('payé', 'Payé'),
        ('annule', 'Annulé')
    ]
    
    montant = models.FloatField()
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_attente')
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    reservation = models.ForeignKey('Reservation', on_delete=models.CASCADE, null=True, blank=True, related_name='paiements')
    numero_facture = models.CharField(max_length=20, unique=True, null=True, blank=True)
    date_facture = models.DateTimeField(null=True, blank=True)

    def generer_numero_facture(self):
        date = datetime.now().strftime('%Y%m%d')
        dernier_numero = Paiement.objects.filter(numero_facture__startswith=date).count()
        return f"{date}-{dernier_numero + 1:04d}"

    def save(self, *args, **kwargs):
        if self.statut == 'payé' and not self.numero_facture:
            self.numero_facture = self.generer_numero_facture()
            self.date_facture = datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paiement {self.id} - {self.membre.nom} {self.membre.prenom} - {self.montant}€"

class Reservation(models.Model):
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    type = models.CharField(max_length=50)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    montant = models.FloatField(default=0)
    validee = models.BooleanField(default=False)
    annulee = models.BooleanField(default=False)
    rattrapage_de = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE, null=True, blank=True)

    def reserver(self):
        pass
    def annuler(self):
        pass
