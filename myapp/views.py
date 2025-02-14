from django.shortcuts import render,redirect
from .models import register_model,Slot
from django.contrib import messages
from django.utils import timezone

# Create your views here.
# def signup(request):
#     return render(request,'signup.html')


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('cpass')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'signup.html')

        if register_model.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'signup.html')

        # Create new user
        register_model.objects.create(username=username, email=email, passw=password)
        messages.success(request, "Signup successful! You can now login.")
        return redirect('login')  # Redirect to the login page

    return render(request, 'signup.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('passw')  # Ensure field name matches your model

        try:
            user = register_model.objects.get(email=email)
            request.session['user_email'] = email 
            if user.passw == password:  # Plaintext comparison (since no hashing was used in signup)
                request.session['user_id'] = user.id  # Store user ID in session
                messages.success(request, "Login successful!")
                return redirect('available_slots')  # Redirect to the home page or dashboard
            else:
                messages.error(request, "Invalid password")
        except register_model.DoesNotExist:
            messages.error(request, "Email not registered")

    return render(request, 'login.html')

def available_slots(request):
    user_email = request.session.get('user_email')
    
    today = timezone.now().date()
    week_end = today + timezone.timedelta(days=6)  # Show slots for the current week

    slots = Slot.objects.filter(
        start_time__date__range=[today, week_end], is_booked=False
    ).order_by("start_time")

    return render(request, "available_slots.html", {"slots": slots,"email":user_email})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import Slot, register_model

from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import Slot, register_model

def book_slot(request, slot_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to book a slot.")
        return redirect('login')

    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    user = get_object_or_404(register_model, email=user_email)  # Ensure correct user instance
    slot = get_object_or_404(Slot, id=slot_id)

    # Prevent booking if the user already booked a slot for the same day
    if Slot.objects.filter(booked_by=user, start_time__date=slot.start_time.date()).exists():
        messages.error(request, "You have already booked a slot for this day.")
        return redirect('available_slots')

    # Ensure slot is not in the past
    if slot.start_time < now():
        messages.error(request, "You cannot book a past slot.")
        return redirect('available_slots')

    slot.is_booked = True
    slot.booked_by = user  # Assign the correct user instance
    slot.save()

    # Send confirmation email
    subject = "Slot Booking Confirmation"
    message = f"Dear {user.username},\n\nYour slot on {slot.start_time.strftime('%Y-%m-%d %H:%M')} has been booked with {slot.teacher.name}."
    email_from = "muskansainicse893@gmail.com"  # Replace with your email
    recipient_list = [user.email]

    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        messages.success(request, f"Slot booked successfully on {slot.start_time.strftime('%Y-%m-%d %H:%M')} with {slot.teacher.name}. Confirmation email sent.")
    except Exception as e:
        messages.error(request, f"Slot booked, but email could not be sent. Error: {str(e)}")

    return redirect('available_slots')


from django.shortcuts import redirect
from django.contrib import messages

def logout(request):
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')  # Redirect to login page
