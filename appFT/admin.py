from django.contrib import admin
from .models import Plan, Trainer, GymMember  # Удалите FitnessPlan из этого импорта

class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class TrainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization')

class GymMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'plan', 'trainer')

admin.site.register(Plan, PlanAdmin)
admin.site.register(Trainer, TrainerAdmin)
admin.site.register(GymMember, GymMemberAdmin)

