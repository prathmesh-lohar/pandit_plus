from django.contrib import admin
from django.urls import path,include
from yajman import views
urlpatterns = [
    
    path("",views.home, name="home"),
    path("register",views.register, name="register"),
    path("login",views.user_login, name="login"),
    path("logout",views.logout, name="logout"),
    path("login_as",views.login_as, name="login_as"),
    path("find_pandit", views.find_pandit, name="find_pandit"),
    path("view_pandit/<int:pandit_id>/<int:pandit_service_id>", views.view_pandit, name="view_pandit"),
    # path("book_pandit/<int:pandit_id>/<int:service_id>", views.book_pandit, name="book_pandit"),
    path("my_bookings", views.my_bookings, name="my_bookings"),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    # Add this line
]
