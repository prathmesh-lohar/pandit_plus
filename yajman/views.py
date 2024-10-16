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

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
        # profile_picture = request.FILES.get('profile_picture')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
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
                # profile_picture=profile_picture
            )
            profile.save()

            
            # Log in the user automatically
            auth_login(request, user)

            messages.success(request, 'Registration successful!')
            return redirect('/')

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('register')

    return render(request, 'yajman/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)  # Django's login function to log in the user
            messages.success(request, 'Logged in successfully!')
            return redirect('/')  # Redirect to home page
        else:
            messages.error(request, 'Invalid username or password!')

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
