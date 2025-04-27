from django.contrib import admin
from .models import register_model, Teacher, Slot,adminregister

# Register your models here.
admin.site.register(register_model)
admin.site.register(Teacher)
admin.site.register(Slot)
admin.site.register(adminregister)

# Unregister the Teacher model first
admin.site.unregister(Teacher)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status')  # Ensure 'status' is in your model

# Register again with the custom admin class
admin.site.register(Teacher, TeacherAdmin)
