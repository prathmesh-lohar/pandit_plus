from django.contrib import admin
from django.urls import path,include
from yajman import views

from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, CustomSetPasswordView


urlpatterns = [
    
    path("",views.home, name="home"),
    path("register",views.register, name="register"),
    path("login",views.user_login, name="login"),
    path("logout",views.logout, name="logout"),
    path("login_as",views.login_as, name="login_as"),
    path("find_pandit", views.find_pandit, name="find_pandit"),
    path("view_pandit/<int:pandit_id>", views.view_pandit, name="view_pandit"),
    # path("book_pandit/<int:pandit_id>/<int:service_id>", views.book_pandit, name="book_pandit"),
    path("my_bookings", views.my_bookings, name="my_bookings"),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('translate_test', views.translate_test, name='translate_test'),
    path('translate', views.translate, name='translate'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),name='password_reset'),
    
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', CustomSetPasswordView.as_view(), name='password_reset_confirm'),
    
    path('reset_done/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
]
