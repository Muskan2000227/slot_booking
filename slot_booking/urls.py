"""
URL configuration for slot_booking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from myapp import views
from myapp.consumers import SlotConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup"),
    path("Login/", views.login, name="login"),
    path("Logout/", views.logout, name="logout"),
    path("available_slots", views.available_slots, name="available_slots"),
    path("book-slot/<int:slot_id>/", views.book_slot, name="book_slot"),
    path("addslotadmin",views.addslotadmin,name="addslotadmin"),
    path('showslotadmin/', views.showslotadmin, name='showslotadmin'),
    path('slots/update/<int:slot_id>/', views.update_slot, name='slot-update'),
    path('slots/delete/<int:slot_id>/', views.delete_slot, name='slot-delete'),
    path("my-slots/", views.my_booked_slots, name="mybookedslots"),
    path("cancel-slot/<int:slot_id>/", views.cancel_slot, name="cancel_slot"),
    path("reschedule-slot/<int:slot_id>/",views.reschedule_slot, name="reschedule_slot"),
    path("adminlogin",views.adminlogin,name="adminlogin"),
    path("logoutadmin",views.logoutadmin,name="logoutadmin"),
    path('counsellorlogin/', views.counsellorlogin, name='counsellorlogin'),
    path('counsellor-logout/', views.counsellor_logout, name='counsellor_logout'),
    path('counsellor-dashboard/', views.counsellor_dashboard, name='counsellor_dashboard'),
    path('slot/', views.slot_view, name='slot_view'),
    path('teachersignup',views.teachersignup,name="teachersignup"),
    path('teacherslots/', views.teacherslots, name='teacherslots'),
    path('update_status/',views.update_status, name='update_status'),
    path('teacher-status/', views.teacher_status, name='teacher_status'),
    path('liveslots', views.liveslots, name='liveslots'),
    path('end-slot/<int:slot_id>/', views.end_slot, name='end-slot'),
    path('get_live_slots', views.get_live_slots, name='get_live_slots'),


]

websocket_urlpatterns = [
    path('ws/slots/', SlotConsumer.as_asgi()),
]
