# Generated by Django 4.2.20 on 2025-05-05 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0003_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='destinataire',
            field=models.CharField(default='admin', max_length=50),
        ),
    ]
