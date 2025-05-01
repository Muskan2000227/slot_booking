# 🎓 Admission Cell Slot Booking System
 This project is a Django-based Slot Booking System that allows users to dynamically book available slots with teachers. It ensures users can book only one slot per day, prevents past slot bookings, and sends confirmation emails upon successful booking.
It uses **Django** for the backend and **HTML/CSS/JavaScript** for the frontend. This system facilitates streamlined slot management for **students**, **teachers**, and **admins** during admission counseling sessions.

---

## 🚀 Features

### 👤 Student Features
- 🔐 Register/Login
- 📅 Book 30-minute counseling slots
- 🔄 Reschedule or ❌ Cancel booked slots
- 📋 View all scheduled appointments

### 👨‍🏫 Teacher Features
- 🔐 Login/Logout
- 📆 View slot schedule
- ✅ Mark status as **Free** or **Busy** (real-time update)
- 📊 Slot-based interaction tracking

### 🛠️ Admin Features
- 🔐 Login/Register teachers
- ➕ Add slots (30-min duration from 10 AM – 4 PM, with 1 PM – 2 PM lunch)
- 🔁 Reschedule or ❌ Cancel student bookings
- 👁️ View live status of all teachers
- 📖 Access student info based on current slots

---

## 🏗️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Django (Python)
- **Database**: SQLite 
- **Deployment**: PythonAnywhere

---
## ⚙️ Getting Started

### Run the following commands to set up the project:

```bash
# Clone the repository
git clone https://github.com/yourusername/slot-booking-system.git
cd slot-booking-system

# Install Django
pip install django

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the development server
python manage.py runserver
➡️ Visit http://127.0.0.1:8000/ in your browser.

