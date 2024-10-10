from django.contrib import admin
from django.urls import path,include
from pandit import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",views.home, name="home"),
    path("/register",views.register, name="register"),
    path("/login",views.user_login, name="login"),
    path("/logout",views.logout, name="logout"),
    path('/update-availability', views.update_availability, name='update_availability'),
    path('/update_profile', views.update_profile, name='update_profile'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('/update-booking/<int:booking_id>', views.update_booking, name='update_booking'),
    path('/my_bookings', views.my_bookings, name='my_bookings'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    