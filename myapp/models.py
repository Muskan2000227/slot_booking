# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.utils import timezone

# Custom User Model
class register_model(models.Model):
    username=models.CharField(max_length=70)
    email=models.EmailField()
    passw=models.CharField(max_length=40)
    cpassw=models.CharField(max_length=40)
    phone_no=models.CharField(max_length=100,blank=True,null=True)
    Address=models.CharField(max_length=100,blank=True,null=True)
    date_of_birth=models.DateField(blank=True,null=True)

    def __str__(self):
        return f"{self.id} - {self.email}"

# Teacher Model
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from datetime import timedelta

class Slot(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(editable=False)  # Prevent manual editing
    teacher = models.ForeignKey("Teacher", on_delete=models.SET_NULL, null=True)
    is_booked = models.BooleanField(default=False)
    booked_by = models.ForeignKey("register_model", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.teacher.name if self.teacher else 'Unassigned'}"

    def clean(self):
        """Ensure start_time is in the future and set end_time automatically."""
        if self.start_time < timezone.now():
            raise ValidationError("Cannot create or book slots for past dates or times.")

        # Automatically set end_time as 30 minutes after start_time
        self.end_time = self.start_time + timedelta(minutes=30)
        # Check if user has already booked a slot for the same day
        if self.is_booked and self.booked_by:
            existing_booking = Slot.objects.filter(
                booked_by=self.booked_by,
                start_time__date=self.start_time.date(),
                is_booked=True
            ).exclude(id=self.id).exists()

            if existing_booking:
                raise ValidationError("You have already booked a slot for this day.")

    def save(self, *args, **kwargs):
        """Before saving, delete past slots"""
        Slot.objects.filter(end_time__lt=timezone.now()).delete()
        super().save(*args, **kwargs)

    def book(self, user):
        """Book the slot and send a confirmation email."""
        if self.start_time < timezone.now():
            raise ValidationError("Cannot book past slots.")

        self.is_booked = True
        self.booked_by = user
        self.save()

        send_mail(
            "Slot Booking Confirmation",
            f"Dear {user.username},\nYour slot on {self.start_time.strftime('%Y-%m-%d %H:%M')} "
            f"has been booked with {self.teacher.name}.",
            "agc@example.com",
            [user.email],
            fail_silently=False,
        )


  

