from django.contrib import admin
from .models import Terrain,Admin
from coach.models import Evenement,Coach
from user.models import Membre
# Register your models here.
admin.site.register(Terrain)
admin.site.register(Admin)
admin.site.register(Evenement)
admin.site.register(Coach)


