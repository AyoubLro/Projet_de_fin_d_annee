# Generated by Django 4.2.20 on 2025-05-09 00:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0006_alter_evenement_lieu_alter_evenement_titre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='id_coach',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='coach.coach'),
        ),
    ]
