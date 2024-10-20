from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from yajman.models import yajman_profile
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from pandit.models import services,pandit_profile,booking,pandit_service
from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookingForm,YajmanProfileForm
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import  ReferralCode  # Ensure you import ReferralCode

from pandit.mail import send_custom_email
from django.urls import reverse_lazy

from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

# Create your views here.


def home(request):
    from pandit.models import services_type
    
    services_type = services_type.objects.all()
    data = {
        'services_type':services_type,
        'active_page': 'home'
    }
    return render(request,"home.html",data)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        # Uncomment if you want to support profile picture upload
        # profile_picture = request.FILES.get('profile_picture')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        # Check if the mobile number already exists in yajman_profile
        if yajman_profile.objects.filter(mobile=mobile).exists():
            messages.error(request, 'Mobile number already exists!')
            return redirect('register')

        try:
            # Create User
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()

            # Create yajman_profile linked to the user
            profile = yajman_profile.objects.create(
                yajman_id=user,
                name=full_name,
                mobile=mobile,
                email=email,
                address=address,
                latitude=latitude,
                longitude=longitude
                # profile_picture=profile_picture  # Uncomment to save the profile picture
            )
            profile.save()

            # Generate a unique referral code
            referral_code = ReferralCode(yajman=user)
            referral_code.generate_code()  # Call the method to generate a unique code
            referral_code.save()

            # Log in the user automatically
            auth_login(request, user)

            messages.success(request, 'Registration successful!')
            mail_sub = "Your Registration Successful"
            mail_body = """now you are yajman in panditplus community, login into your dashboard and make status .
            https://panditplus.in/login"""
            
            
            send_custom_email(to_email=email, subject=mail_sub, body=mail_body)
            return redirect('/')

        except ValidationError as e:
            messages.error(request, f'Error during registration: {str(e)}')
            return redirect('register')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')
            return redirect('register')

    return render(request, 'yajman/register.html')


def user_login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')  # Use mobile instead of username
        password = request.POST.get('password')

        try:
            # Find the user linked to the mobile number
            profile = yajman_profile.objects.get(mobile=mobile)
            user = profile.yajman_id  # Get the User instance associated with the profile

            # Authenticate the user
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user is not None:
                # Log in the user
                login(request, authenticated_user)  # Django's login function
                messages.success(request, 'Logged in successfully!')
                return redirect('/')  # Redirect to home page
            else:
                messages.error(request, 'Invalid mobile number or password!')

        except yajman_profile.DoesNotExist:
            messages.error(request, 'Mobile number not found!')

    return render(request, 'yajman/login.html')


def logout(request):
    auth_logout(request)  # Log out the user
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')


@login_required
def test():
    pass

def login_as(request):
    
    return render(request, "yajman/login_as.html")


@login_required
def find_pandit(request):
    # Get all available services for the dropdown
    all_services = services.objects.all()

    # Get the search parameters from the request
    location = request.GET.get('location')
    pooja_type = request.GET.get('pooja_type')
    budget = request.GET.get('budget')

    # Start with all available pandits
    pandits = pandit_profile.objects.filter(availability='availabe')

    # Log the initial set of pandits
    print("Initial Pandits:", pandits)

    # Exclude pandits that the current yajman has already booked
    booked_pandits = booking.objects.filter(yajman_id=request.user).values_list('name_of_pooja__pandit_id', flat=True)
    
    print("Booked Pandits IDs:", booked_pandits)  # Log booked pandit IDs for debugging

    # Apply exclusion for already booked pandits
    pandits = pandits.exclude(pandit_id__in=booked_pandits)
    
    # Log pandits after exclusion
    print("Pandits after exclusion:", pandits)

    # Apply additional filters
    if location:
        pandits = pandits.filter(address__icontains=location)
        print("Pandits after location filter:", pandits)

    if pooja_type:
        pandits = pandits.filter(pandit_id__pandit_service__service__id=pooja_type)
        print("Pandits after pooja type filter:", pandits)

    if budget:
        budget_range = budget.split('-')
        if len(budget_range) == 2:
            min_budget, max_budget = map(int, budget_range)
            pandits = pandits.filter(pandit_id__pandit_service__rate__gte=min_budget, pandit_id__pandit_service__rate__lte=max_budget)
        else:
            pandits = pandits.filter(pandit_id__pandit_service__rate__lte=int(budget))
        print("Pandits after budget filter:", pandits)

    # Remove duplicates
    pandits = pandits.distinct()

    # Prepare the list of pandits and their services
    pandit_services = []
    for pandit in pandits:
        services_offered = pandit.pandit_id.pandit_service_set.all()
        
        # Log services for debugging
        print(f"Services for pandit {pandit.pandit_id.username}: {services_offered}")
        
        for service in services_offered:
            pandit_services.append({
                'pandit': pandit,
                'service': service,
               
            })

    context = {
        'services': all_services,
        'pandit_services': pandit_services,
         'active_page': 'find_pandit'
    }

    # Log the final pandit services data
    print("Final Pandit Services:", pandit_services)

    return render(request, "yajman/find_pandit.html", context)


# @login_required
# def book_pandit(request, pandit_id,service_id):
#     pandit = get_object_or_404(User, pk=pandit_id)
#     yajman = request.user  # The logged-in user
#     service = get_object_or_404(pandit_service, id=service_id) 
#     # Check if a booking already exists for the Yajman and Pandit
#     existing_booking = booking.objects.filter(yajman_id=yajman, pandit_id=pandit).first()

#     if existing_booking:
#         # If a booking already exists, do not create a new one
#         if existing_booking.status == 'requested':
#             # Return or redirect to the appropriate page if already requested
#             return redirect('find_pandit')  # Assuming 'find_pandit' is the page you want to redirect to
#     else:
#         # Create a new booking with the status 'requested'
#         new_booking = booking.objects.create(
#             yajman_id=yajman,
#             pandit_id=pandit,
#             status='requested',
#             payment_status='not_received',  # Assuming this is the default
#             services_id=service
#         )
#         new_booking.save()
#         messages.success(request, "Request send to pandit wait to conform and then make payment")

#     return redirect('find_pandit')  # Redirect after booking
    

@login_required
def my_bookings(request):
    # Get the user's bookings
    user_bookings = booking.objects.filter(yajman_id=request.user)

    context = {
        'user_bookings': user_bookings,
        'active_page': 'my_bookings'
    }

    return render(request, "yajman/my_bookings.html", context)


@login_required
def cancel_booking(request, booking_id):
    booking_instance = get_object_or_404(booking, id=booking_id, yajman_id=request.user)
    print(booking_instance)
    
    # Optionally check the status before allowing cancellation
    # if booking_instance.status not in ['conformed', 'on_hold']:
    #     messages.error(request, "Cancellation is not allowed for this booking.")
    #     return redirect('my_bookings')

    booking_instance.delete()  # Delete the booking
    messages.success(request, "Booking cancelled successfully.")  # Add success message

    return redirect('my_bookings') 


@login_required
def view_pandit(request, pandit_id, pandit_service_id):
    pandit = get_object_or_404(User, pk=pandit_id)

    yajman = request.user  # The logged-in user
    service = get_object_or_404(pandit_service, id=pandit_service_id)
    services_provide = pandit_service.objects.filter(pandit_id=pandit_id)

    # Check if a booking already exists for the Yajman and Pandit
    existing_booking = booking.objects.filter(yajman_id=yajman, pandit_id=pandit, name_of_pooja=service).first()  # Assuming `name` is the field name for the service

    if request.method == 'POST':
        # Handle form submission
        form = BookingForm(request.POST)
        if form.is_valid():
            if not existing_booking:
                # Create a new booking and set the foreign keys and statuses
                new_booking = form.save(commit=False)
                new_booking.yajman_id = yajman
                new_booking.pandit_id = pandit
                new_booking.services = service
                new_booking.status = 'requested'          # Set status to 'requested'
                new_booking.payment_status = 'not_received'  # Set payment status to 'not_received'
                new_booking.save()
                messages.success(request, "Request sent to pandit. Please wait for confirmation before making payment.")
                
                
                mail_sub_pandit = "you got new order reach to yajman and conform date and ask for payment compltion"
                mail_body_pandit = "Yajman :"+request.user.username+"pooja : "+service.service.service_name
                
                
                send_custom_email(to_email=pandit.email, subject=mail_sub_pandit, body=mail_body_pandit)
                
                
                
            else:
                messages.info(request, "You have already requested this pandit for the selected service.")

            return redirect('find_pandit')  # Redirect after booking
    else:
        # Pass the service name or ID to the form
        form = BookingForm(name_of_pooja=service)  # Use service.name if it represents the pooja name

    return render(request, "yajman/view_pandit.html", {
        'pandit': pandit,
        'service': service,
        'form': form,
        'services_provide':services_provide,
        'active_page': 'view_pandit'
    })



def translate_test(request):
    return render(request, "translate_test.html")

@csrf_exempt  # Only use if necessary for testing, consider proper CSRF protection in production
def translate(request):
    if request.method == 'POST':
        url = 'https://libretranslate.de/translate'
        data = {
            'q': request.POST.get('text'),  # Text to translate
            'source': request.POST.get('source_lang', 'en'),  # Default source language
            'target': request.POST.get('target_lang', 'es'),  # Default target language
            'format': 'text'
        }
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return JsonResponse(response.json())  # Return the translated text
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)





class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/custom_password_reset_email.html'
    subject_template_name = 'registration/custom_password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        # Custom email logic
        email = form.cleaned_data.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            # Generate token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset URL
            reset_url = self.request.build_absolute_uri(
                reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Prepare email content
            mail_sub = 'Password Reset Request'
            html_content = render_to_string('registration/custom_password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            plain_content = render_to_string('registration/custom_password_reset_email.txt', {
                'user': user,
                'reset_url': reset_url,
            })

            # Send email using your custom function
            send_custom_email(to_email=user.email, subject=mail_sub, body=plain_content, html_content=html_content)

        return super().form_valid(form)
    
    
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'

class CustomSetPasswordView(PasswordResetConfirmView):
    template_name = 'set_password.html'
