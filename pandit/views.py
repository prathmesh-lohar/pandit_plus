from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from pandit.models import pandit_profile
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import PanditProfileForm
# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST


from django.shortcuts import render, redirect, get_object_or_404
from pandit.models import pandit_profile, pandit_service,booking
from .forms import PanditProfileForm

from django.shortcuts import render, redirect, get_object_or_404

from .forms import PanditProfileForm,Pandit_availability_form,PanditServiceForm,BookingForm
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

from pandit.mail import send_custom_email

@login_required
def home(request):
    try:
        # Get the logged-in user's pandit_profile
        profile = pandit_profile.objects.get(pandit_id=request.user)
    except pandit_profile.DoesNotExist:
        # If no pandit_profile exists, show a message and redirect to /pandit/login
        messages.error(request, "No pandit profile available. Please register.")
        return redirect('/pandit/login')

    # Get the user's pandit_service instances
    user_services = pandit_service.objects.filter(pandit_id=request.user)

    # Handle the PanditServiceForm for adding new services
    if request.method == 'POST':
        form = PanditServiceForm(request.POST)
        if form.is_valid():
            pandit_service_instance = form.save(commit=False)
            pandit_service_instance.pandit_id = request.user  # Assign the logged-in user as pandit_id
            pandit_service_instance.save()
            return redirect('home')  # Redirect to the home page after saving
    else:
        form = PanditServiceForm()

    # Get all bookings for the pandit
    bookings = booking.objects.filter(pandit_id=request.user)
    
    

    data = {
        'pandit_service': user_services,
        'profile': profile,
        'form': form,  # Form for adding new services
        'bookings': bookings,  # List of bookings
    }
    return render(request, "pandit/home.html", data)


@login_required
def update_booking(request, booking_id):
    # Fetch the booking that needs to be updated
    booking_to_update = get_object_or_404(booking, id=booking_id, pandit_id=request.user)

    if request.method == 'POST':
        update_form = BookingForm(request.POST, instance=booking_to_update)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Booking updated successfully.")
            return redirect('home')
        else:
            messages.error(request, f"Failed to update booking. Errors: {update_form.errors}")
    else:
        update_form = BookingForm(instance=booking_to_update)

    data = {
        'update_form': update_form,
        'booking': booking_to_update,
    }
    return render(request, 'pandit/update_booking.html', data)


@csrf_exempt  # Ensure CSRF protection is handled if needed
def update_availability(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            availability = body.get('availability')

            if availability in ['available', 'busy']:
                # Assuming pandit_profile is the model for your profiles
                profile = get_object_or_404(pandit_profile, pandit_id=request.user.id)
                profile.availability = availability
                profile.save()
                return JsonResponse({'status': 'success', 'availability': availability})

            return JsonResponse({'status': 'error', 'message': 'Invalid availability status'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from .models import pandit_profile  # Ensure this imports your pandit_profile model

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
        experience = request.POST.get('experience')
    
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('/pandit/register')

        # Check if the mobile number already exists in pandit_profile
        if pandit_profile.objects.filter(mobile=mobile).exists():
            messages.error(request, 'Mobile number already exists!')
            return redirect('/pandit/register')

        try:
            # Create User (only with fields supported by the User model)
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()

            # Create pandit_profile linked to the user
            profile = pandit_profile.objects.create(
                pandit_id=user,  # link to the User instance
                name=full_name,
                mobile=mobile,
                email=email,
                address=address,
                latitude=latitude,  # store latitude in pandit_profile
                longitude=longitude,  # store longitude in pandit_profile
                Exp=experience  # store experience in pandit_profile
            )
            profile.save()

            # Log in the user automatically
            auth_login(request, user)

            messages.success(request, 'Registration successful!')
            
            mail_sub = "Your Registration Successful"
            mail_body = """now you are pandit in panditplus community, login into your dashboard and make status online if you are
            ailable and offline if you busy .
            https://panditplus.in/pandit/login"""
            
            
            send_custom_email(to_email=email, subject=mail_sub, body=mail_body)
            
            return redirect('/pandit')

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('/pandit/register')

    return render(request, 'pandit/register.html')



def user_login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')  # Retrieve mobile number
        password = request.POST.get('password')

        try:
            # Find the user associated with this mobile number
            profile = pandit_profile.objects.get(mobile=mobile)
            user = profile.pandit_id  # Get the related User instance

            # Authenticate the user using the username and password
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                # Log in the user
                login(request, user)  # Django's login function to log in the user
                messages.success(request, 'Logged in successfully!')
                return redirect('/pandit')  # Redirect to home page
            else:
                messages.error(request, 'Invalid mobile number or password!')

        except pandit_profile.DoesNotExist:
            messages.error(request, 'Mobile number not found!')

    return render(request, 'pandit/login.html')
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # Authenticate the user
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             # Log in the user
#             login(request, user)  # Django's login function to log in the user
#             messages.success(request, 'Logged in successfully!')
#             return redirect('/pandit')  # Redirect to home page
#         else:
#             messages.error(request, 'Invalid username or password!')

#     return render(request, 'pandit/login.html')

def logout(request):
    auth_logout(request)  # Log out the user
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/pandit')

@login_required
def update_availability(request):
    # Log the request method
    print(f"Request method: {request.method}")

    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            print(f"Data received: {data}")
        except json.JSONDecodeError as e:
            # Log JSON parsing errors
            print(f"JSONDecodeError: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        # Fetch the profile based on the current logged-in user
        profile = get_object_or_404(pandit_profile, pandit_id=request.user)
        print(f"Profile found: {profile}")

        # Get the 'availability' field from the parsed data
        availability = data.get('availability')
        print(f"Availability received: {availability}")

        # Validate the availability value
        if availability in ['available', 'busy']:
            profile.availability = availability  # Update the availability status
            profile.save()

            print(f"Profile updated to: {availability}")
            # Return a success response
            return JsonResponse({'status': 'success', 'availability': availability})
        else:
            # Log invalid availability values
            print(f"Invalid availability status: {availability}")
            return JsonResponse({'status': 'error', 'message': 'Invalid availability status.'}, status=400)
    
    # Log non-POST requests
    print(f"Invalid request method: {request.method}")
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def update_profile(request):
    profile = request.user.pandit_profile  # Assuming a one-to-one relationship with the User model

    if request.method == 'POST':
        profile.name = request.POST['name']
        profile.last_name = request.POST['last_name']
        profile.mobile = request.POST['mobile']
        profile.alternative_mobile = request.POST['alternative_mobile']
        profile.email = request.POST['email']
        profile.dob = request.POST['dob']
        profile.education = request.POST['education']
        profile.college = request.POST['college']
        profile.Exp = request.POST['Exp']
        profile.address = request.POST['addreess']
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('/pandit#profile')  # Redirect to the profile page

    return redirect('/pandit#profile')

@login_required
def update_profile_picture(request):
   
    if request.method == 'POST':
        profile = request.user.pandit_profile  # Assuming there's a one-to-one relationship
        profile.profile_picture = request.FILES.get('profile_picture')  # Get the uploaded file
        profile.save()  # Save the profile with the new picture

        messages.success(request, 'Profile Picture updated successfully!')

        return JsonResponse({'status': 'success', 'profile_picture': profile.profile_picture.url})
    
    return JsonResponse({'status': 'invalid_method'}, status=405)


@login_required
def create_or_update_service(request):
    if request.method == 'POST':
        form = PanditServiceForm(request.POST)
        if form.is_valid():
            pandit_service_instance = form.save(commit=False)
            pandit_service_instance.pandit_id = request.user  # Assign the logged-in user as pandit_id
            pandit_service_instance.save()
            return redirect('success_url')  # Replace with your success URL
    else:
        form = PanditServiceForm()
    
    return render(request, 'your_template.html', {'form': form})


@login_required
def my_bookings(request):
    from pandit.models import booking
    bookings = booking.objects.filter(pandit_id=request.user)

    # Convert the bookings into the format FullCalendar expects
    events = []
    for booking in bookings:
        title = booking.name_of_pooja.service.service_name if booking.name_of_pooja and booking.name_of_pooja.type_of_pooja else 'No Pooja Name'
        description = f"Pooja: {title} at {booking.locattion}"  # Fixed typo here

        # Validate and format dates and times
        start_date = booking.conform_date.isoformat() if booking.conform_date else '1970-01-01'  # Default date
        start_time = booking.conform_time.isoformat() if booking.conform_time else '00:00'  # Default time

        # Combine date and time into a single string in ISO format
        start_datetime = f"{start_date}T{start_time}"  # FullCalendar expects ISO 8601 format

        events.append({
            'title': title,
            'start': start_datetime,  # Use 'start' for FullCalendar
            'description': description,
            'status': booking.status,
        })

    return JsonResponse(events, safe=False)
