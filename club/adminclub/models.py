from django.db import models

# Create your models here.

class Admin(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='admin')
    
    def gerer_horaires(self):
        pass
    def gerer_evenements(self):
        pass
    def gerer_paiements(self):
        pass
    def gerer_employes(self):
        pass

class Terrain(models.Model):
    nom = models.CharField(max_length=100)
    disponibilite = models.BooleanField(default=True)
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', null=True, blank=True)
    prix = models.FloatField(default=0)
    def reserver(self):
        pass
    def verifier(self):
        pass
