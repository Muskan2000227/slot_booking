from django.shortcuts import render,redirect
from .models import register_model,Slot,Teacher
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.core.mail import send_mail
from datetime import timedelta

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


def book_slot(request, slot_id):
    if not request.user.is_authenticated:
        return redirect('login')

    user_email = request.session.get('user_email')
    if not user_email:
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


def logout(request):
    return redirect('login')  # Redirect to login page


def addslotadmin(request):
    if request.method == "POST":
        start_time = request.POST.get("start_time")
        teacher_id = request.POST.get("teacher")

        if not start_time or not teacher_id:
            messages.error(request, "Please fill all fields.")
            return redirect("addslotadmin")

        # Convert start_time to timezone-aware datetime object
        start_time = timezone.datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        start_time = timezone.make_aware(start_time)

        # Get the selected teacher
        teacher = Teacher.objects.get(id=teacher_id)

        # Create slot
        slot = Slot.objects.create(
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30),
            teacher=teacher,
            is_booked=False
        )
        
        messages.success(request, "Slot added successfully!")
        return redirect("addslotadmin")

    #  #Fetch available teachers and slots
    teachers = Teacher.objects.all()
    slots = Slot.objects.all().order_by("start_time")  # Show upcoming slots first

    return render(request, "addslotadmin.html",{'teachers':teachers})

def showslotadmin(request):
    teachers = Teacher.objects.all()
    slots = Slot.objects.all().order_by("start_time")
    print("Teachers found:", teachers)  # Debugging
    return render(request, 'showslotadmin.html', {"teachers": teachers, "slots": slots})


def update_slot(request, slot_id):
    """Update a slot without Django Forms"""
    slot = get_object_or_404(Slot, id=slot_id)

    if request.method == "POST":
        slot.start_time = request.POST.get("start_time")
        slot.end_time = request.POST.get("end_time")
        teacher_id = request.POST.get("teacher")
        slot.teacher = get_object_or_404(Teacher, id=teacher_id)
        slot.is_booked = True if request.POST.get("is_booked") == "on" else False
        
        slot.save()
        return redirect('showslotadmin')  

    teachers = Teacher.objects.all()
    return render(request, 'update_slot.html', {'slot': slot, 'teachers': teachers})

def delete_slot(request, slot_id):
    """Delete a slot"""
    slot = get_object_or_404(Slot, id=slot_id)
    
    if request.method == "POST":
        slot.delete()
        return redirect('showslotadmin')

    return render(request, 'delete_confirm.html', {'slot': slot})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Slot, register_model  # ✅ Import register_model

def my_booked_slots(request):
    """Show slots booked by the logged-in user based on email"""
    user_email = request.session.get('user_email')

    if not user_email:
        messages.error(request, "User email not found. Please log in.")
        return redirect("login")  # Redirect to login if email is missing

    try:
        user = register_model.objects.get(email=user_email)  # ✅ Fetch user from register_model
    except register_model.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect("login")

    # ✅ Filter slots where the user has booked them
    user_slots = Slot.objects.filter(booked_by=user).order_by("start_time")

    return render(request, "mybookedslots.html", {"slots": user_slots})



from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from .models import Slot, register_model

def cancel_slot(request, slot_id):
    """Allow user to cancel a booked slot based on email and send cancellation email."""
    user_email = request.session.get("user_email")

    if not user_email:
        messages.error(request, "User email not found. Please log in.")
        return redirect("login")  # Redirect if email is missing

    user = get_object_or_404(register_model, email=user_email)  # ✅ Get user from register_model
    slot = get_object_or_404(Slot, id=slot_id, booked_by=user)  # ✅ Ensure the slot belongs to the logged-in user

    # ✅ Store slot details before cancellation
    teacher_name = slot.teacher.name
    start_time = slot.start_time
    end_time = slot.end_time

    # ✅ Cancel the booking
    slot.booked_by = None  
    slot.is_booked = False  # Optional: Mark slot as available
    slot.save()

    # ✅ Send cancellation email
    send_mail(
        "Your Slot Has Been Canceled",
        f"Dear {user.username},\n\nYour slot with {teacher_name} on {start_time} - {end_time} has been successfully canceled.\n\nThank you!",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    messages.success(request, "Your slot has been canceled successfully. A confirmation email has been sent.")
    return redirect("mybookedslots")



from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Slot, register_model
from django.conf import settings

def reschedule_slot(request, slot_id):
    """Allow a user to reschedule a booked slot and notify via email."""
    user_email = request.session.get("user_email")
    user = get_object_or_404(register_model, email=user_email)

    slot = get_object_or_404(Slot, id=slot_id, booked_by=user)

    if request.method == "POST":
        new_slot_id = request.POST.get("new_slot")
        new_slot = get_object_or_404(Slot, id=new_slot_id, is_booked=False)
 
        # Release old slot
        slot.booked_by = None
        slot.is_booked = False
        slot.save()

        # Assign new slot
        new_slot.booked_by = user
        new_slot.is_booked = True
        new_slot.save()

        # Send email for new slot confirmation
        send_mail(
            "Your Slot Has Been Rescheduled",
            f"Dear {user.username},\n\nYou have successfully rescheduled your slot to {new_slot.start_time} - {new_slot.end_time} with {new_slot.teacher.name}.\n\nThank you!",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        messages.success(request, "Your slot has been successfully rescheduled. A confirmation email has been sent.")
        return redirect("mybookedslots")

    available_slots = Slot.objects.filter(is_booked=False)
    return render(request, "reschedule_slot.html", {"slot": slot, "available_slots": available_slots})

