from django.shortcuts import render,redirect
from .models import register_model,Slot,Teacher,adminregister
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.core.mail import send_mail
from datetime import timedelta
from django.contrib.auth import logout


def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('cpass')

        if password != confirm_password:
            msg="Passwords do not match"
            return render(request, 'signup.html',{"message":msg})

        if register_model.objects.filter(email=email).exists():
            msg="Email already exists"
            return render(request, 'signup.html',{"message":msg})

        # Create new user
        register_model.objects.create(username=username, email=email, passw=password)
        return redirect('login')  # Redirect to the login page

    return render(request, 'signup.html')

  

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('passw')  # Ensure field name matches your model

        try:
            user = register_model.objects.get(email=email)  # Fetch user by email
            if user.passw == password:  # Check password (not hashed)
                request.session['user_id'] = user.id  # Store user ID in session
                request.session['user_email'] = user.email  # Store user email in session
                return redirect('available_slots')  # Redirect to dashboard
            else:
                
                return redirect('login')  # Stay on login page if password is wrong

        except register_model.DoesNotExist:
            return redirect('login')  # Stay on login page if email is wrong

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
    if not request.session.has_key('email'):
        return redirect('login')
    
    del request.session['email']
    return redirect('login')


from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from .models import Teacher, Slot

def addslotadmin(request):
    context = {"messages": {}, "teachers": Teacher.objects.all()}  # Ensure teachers are passed

    if request.method == "POST":
        start_time = request.POST.get("start_time")
        teacher_id = request.POST.get("teacher")

        if not start_time or not teacher_id:
            context["messages"]["error"] = "Please fill all fields."
            return render(request, "addslotadmin.html", context)

        # Convert start_time to timezone-aware datetime object
        start_time = timezone.datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        start_time = timezone.make_aware(start_time)

        # Get the selected teacher
        teacher = get_object_or_404(Teacher, id=teacher_id)

        # Check if a slot for this teacher already exists at the same time
        existing_slot = Slot.objects.filter(teacher=teacher, start_time=start_time).exists()
        if existing_slot:
            context["messages"]["error"] = "Cannot add this slot. A slot for this teacher already exists at this time."
            return render(request, "addslotadmin.html", context)

        # Create slot
        Slot.objects.create(
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30),
            teacher=teacher,
            is_booked=False
        )

        context["messages"]["success"] = "Slot added successfully!"
        return render(request, "addslotadmin.html", context)

    return render(request, "addslotadmin.html", context)


from django.shortcuts import render
from .models import Teacher, Slot
from django.utils import timezone

def showslotadmin(request):
    teachers = Teacher.objects.all()
    
    # Get current datetime
    now = timezone.now()
    
    # Filter slots that start today or in the future
    slots = Slot.objects.filter(
        start_time__date__gte=now.date()  # Compare date part only
    ).order_by("start_time")
    
    print("Teachers found:", teachers)  # Debugging
    print("Current date:", now.date())  # Debugging
    print("Slots count:", slots.count())  # Debugging
    
    return render(request, 'showslotadmin.html', {
        "teachers": teachers, 
        "slots": slots
    })


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

    return render(request, "mybookedslots.html", {"slots": user_slots,"email":user_email})



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

def adminlogin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('passw')
        # Check if the user exists in the database
        try:
            admin = adminregister.objects.get(email=email, passw=password)
            messages.success(request, "Login successful!")
            return redirect('addslotadmin')  # Redirect to the admin dashboard page
        except adminregister.DoesNotExist:
            messages.error(request, "Invalid email or password!")
    
    return render(request, 'adminlogin.html')


def logoutadmin(request):
    logout(request) 
    return render(request,'signup.html')
    
#Teacher Login
def counsellorlogin(request):
    return render(request,'counsellorlogin.html') 

from django.shortcuts import render
from .models import Teacher  # Ensure this import exists

def teachersignup(request):
    context = {}  # Dictionary to store messages

    if request.method == "POST":
        name = request.POST.get('username')  # Changed 'username' to 'name'
        email = request.POST.get('email')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('cpass')

        if password != confirm_password:
            context['message'] = "Passwords do not match"
            return render(request, 'teachersignup.html', context)  # Stay on the same page

        if Teacher.objects.filter(email=email).exists():
            context['message'] = "Email already exists"
            return render(request, 'teachersignup.html', context)  # Stay on the same page

        # Create a new user without hashing the password (not recommended for production)
        Teacher.objects.create(name=name, email=email, password=password)
        context['message'] = "Signup successful! You can now login."

    return render(request, 'teachersignup.html', context)



from django.shortcuts import render, redirect
from .models import Teacher

def counsellorlogin(request):
    context = {}  # Dictionary to store messages

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('passw')

        print("Email Entered:", email)
        print("Password Entered:", password)

        try:
            teacher = Teacher.objects.get(email=email, password=password)
            print("Teacher Found:", teacher.name)

            request.session['teacher_id'] = teacher.id  
            context['success'] = "Login successful!"
            return redirect('teacherslots')  # Redirect after login

        except Teacher.DoesNotExist:
            print("Invalid Credentials!")
            context['error'] = "Invalid email or password!"

    return render(request, 'counsellorlogin.html', context)




def counsellor_logout(request):
    if 'counsellor_id' in request.session:
        request.session.flush()  # Clear session
    return redirect('counsellorlogin')


def counsellor_dashboard(request):
    teacher = Teacher.objects.get(id=request.user.id)
    return render(request, 'counsellor_dashboard.html', {'current_status': teacher.status})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.db import transaction

@csrf_exempt
@require_POST
def update_status(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        teacher = Teacher.objects.get(id=request.session['teacher_id'])
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['Free', 'Busy']:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
        teacher.status = new_status
        teacher.save()
        
        return JsonResponse({
            'success': True,
            'new_status': teacher.status,
            'status_display': teacher.get_status_display()
        })
        
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def slot_view(request):
    return render(request, 'slot.html')


from django.shortcuts import render, redirect
from .models import Teacher, Slot
from django.utils import timezone  # For timezone-aware datetime

def teacherslots(request):
    context = {}

    # Check if the teacher is logged in
    if 'teacher_id' not in request.session:
        return redirect('teacherlogin')

    teacher_id = request.session['teacher_id']
    teacher = Teacher.objects.get(id=teacher_id)

    # Get current datetime
    now = timezone.now()
    
    # Fetch slots assigned to the teacher that are in the future, ordered by start_time
    slots = Slot.objects.filter(
        teacher=teacher,
        start_time__gte=now  # Only slots starting now or in the future
    ).order_by('start_time')

    context['teacher'] = teacher
    context['slots'] = slots

    return render(request, 'teacherslots.html', context)


# # Update status of teacher
# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from .models import Teacher

# def update_status(request):
#     if request.method == "POST":
#         teacher_id = request.POST.get("teacher_id")
#         status = request.POST.get("status")

#         print(f"Received Teacher ID: {teacher_id}")  # Debugging
#         print(f"Received Status: {status}")  # Debugging

#         if not teacher_id or teacher_id == "0":  
#             return JsonResponse({"success": False, "error": "Invalid teacher ID"})

#         try:
#             teacher = get_object_or_404(Teacher, id=int(teacher_id))
#             print(f"Fetched Teacher from DB: {teacher}")  # Debugging
            
#             teacher.status = status
#             teacher.save()
#             print(f"Updated Teacher Status: {teacher.status}")  # Debugging
            
#             return JsonResponse({"success": True, "status": teacher.status})
#         except Exception as e:
#             print(f"Error updating status: {str(e)}")  # Debugging
#             return JsonResponse({"success": False, "error": str(e)})

#     return JsonResponse({"success": False, "error": "Invalid request"})

def teacher_status(request):
    teachers = Teacher.objects.all()
    return render(request, 'teacher_status.html', {'teachers': teachers})



# Live
# import pytz
# from django.http import JsonResponse
# from django.utils.timezone import now, localtime
# from datetime import timedelta
# from .models import Slot  # Import your Slot model

# def get_live_slots(request):
#     """Fetch slots where the current time is within the slot's duration (start to end time)."""
#     ist = pytz.timezone('Asia/Kolkata')  # Define IST timezone
#     current_time = localtime(now(), ist).replace(second=0, microsecond=0)  # Convert to IST
    
#     print(f"Current time in IST: {current_time}")  # Debugging log

#     # Find slots where current time is between start_time and end_time
#     live_slots = Slot.objects.filter(
#         start_time__lte=current_time,
#         end_time__gte=current_time,
#         is_booked=True
#     )

#     data = []
#     for slot in live_slots:
#         data.append({
#             "student": slot.booked_by.username,
#             "teacher": slot.teacher.name,
#             "start_time": localtime(slot.start_time, ist).strftime("%I:%M %p"),
#             "end_time": localtime(slot.end_time, ist).strftime("%I:%M %p"),
#             "time_remaining": str(slot.end_time - current_time),  # Add remaining time
#         })

#     return JsonResponse({"slots": data})


from django.http import JsonResponse
from django.utils.timezone import now, localtime
import pytz
from django.contrib.auth.decorators import user_passes_test
from .models import Slot

def get_live_slots(request):
    """Fetch slots where current time is within slot duration"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = localtime(now(), ist)
    
    live_slots = Slot.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_booked=True
    )

    data = []
    for slot in live_slots:
        slot_data = {
            "id": slot.id,
            "student": slot.booked_by.username,
            "teacher": slot.teacher.name,
            "start_time": localtime(slot.start_time, ist).strftime("%I:%M %p"),
            "end_time": localtime(slot.end_time, ist).strftime("%I:%M %p"),
            "time_remaining": str(slot.end_time - current_time),
            "can_end": request.user.is_staff,  # Flag showing if current user can end slot
        }
        data.append(slot_data)

    return JsonResponse({"slots": data})

@user_passes_test(lambda u: u.is_staff)
def end_slot(request, slot_id):
    """Admin endpoint to force-end a slot"""
    try:
        slot = Slot.objects.get(id=slot_id)
        slot.end_time = localtime(now())  # Set end time to now
        slot.save()
        return JsonResponse({"success": True, "message": "Slot ended successfully"})
    except Slot.DoesNotExist:
        return JsonResponse({"success": False, "message": "Slot not found"}, status=404)



def liveslots(request):
    return render(request,'liveslots.html')