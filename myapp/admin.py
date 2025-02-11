from django.contrib import admin
from .models import register_model, Teacher, Slot

# Register your models here.
admin.site.register(register_model)
admin.site.register(Teacher)
admin.site.register(Slot)

