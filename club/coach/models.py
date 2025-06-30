from django.db import models
from user.models import Membre
from datetime import datetime

# Create your models here.

class Coach(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    motdepasse = models.CharField(max_length=128, null=True, blank=True)
    def gerer_membres_club(self):
        pass
    def gerer_horaires_entrainement(self):
        pass
    def envoyer_licences_certificats(self):
        pass
    def verifier_terrains(self):
        pass
    def __str__(self):
        return f"{self.nom} {self.prenom}"  

class Evenement(models.Model):
    titre = models.CharField(max_length=100)
    date = models.DateField()
    lieu = models.CharField(max_length=100)
    participants = models.ManyToManyField(Membre, related_name='evenements_participes', through='ParticipationEvenement')

    def __str__(self):
        return self.titre

    def nombre_participants(self):
        return self.participants.count()

    def est_complet(self):
        return self.nombre_participants() >= self.participants_max if hasattr(self, 'participants_max') else False

class ParticipationEvenement(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('inscrit', 'Inscrit'),
        ('present', 'Présent'),
        ('absent', 'Absent')
    ], default='inscrit')

    class Meta:
        unique_together = ('membre', 'evenement')

class Document(models.Model):
    fichier = models.FileField(upload_to='documents/')
    type = models.CharField(max_length=50, choices=[('licence', 'Licence'), ('certificat', 'Certificat')])
    date_envoi = models.DateTimeField(auto_now_add=True)
    destinataire = models.CharField(max_length=50, default='admin')
    id_coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)

class Facture(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée')
    ]

    numero = models.CharField(max_length=20, unique=True)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='factures')
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='factures')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    def __str__(self):
        return f"Facture {self.numero} - {self.membre.nom} {self.membre.prenom}"

    def generer_numero(self):
        date = datetime.now().strftime('%Y%m%d')
        dernier_numero = Facture.objects.filter(numero__startswith=date).count()
        return f"{date}-{dernier_numero + 1:04d}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generer_numero()
        super().save(*args, **kwargs)
