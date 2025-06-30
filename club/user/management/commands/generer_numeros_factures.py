from django.core.management.base import BaseCommand
from user.models import Paiement

class Command(BaseCommand):
    help = 'Génère les numéros de facture pour les paiements validés sans numéro de facture.'

    def handle(self, *args, **kwargs):
        paiements = Paiement.objects.filter(statut='valide', numero_facture__isnull=True)
        total = paiements.count()
        for paiement in paiements:
            paiement.save()  # Déclenche la génération du numéro de facture
        self.stdout.write(self.style.SUCCESS(f'{total} paiements mis à jour avec un numéro de facture.')) 