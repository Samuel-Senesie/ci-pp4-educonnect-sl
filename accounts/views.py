from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils.crypto import get_random_string
from .models import UserProfile, CustomUser
from .forms import CustomUserCreationForm, CustomLoginForm, UserProfileForm
from datetime import date, time, datetime
from django.views.decorators.csrf import csrf_protect
from twilio.rest import Client
import logging 


logger = logging.getLogger(__name__) #Debug

# Create your views here.
#def welcome_view(request):
    #return render(request, 'home/welcome.html')

#  Registration view
def signup(request):
    """
    User registration view with form validation
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data.copy()
            # Convert date/time fields to strings for session storage
            if 'date_of_birth' in cleaned_data and isinstance(cleaned_data['date_of_birth'], date):
                cleaned_data['date_of_birth'] = cleaned_data['date_of_birth'].isoformat()
            
            if 'preferred_time_from' in cleaned_data and isinstance(cleaned_data['preferred_time_from'], time):
                cleaned_data['preferred_time_from'] = cleaned_data['preferred_time_from'].isoformat()
            if 'preferred_time_to' in cleaned_data and isinstance(cleaned_data['preferred_time_to'], time):
                cleaned_data['preferred_time_to'] = cleaned_data['preferred_time_to'].isoformat()

            request.session['signup_data'] = cleaned_data  # Save the data session
            return redirect('accounts:signup_review')
        else:
            print("Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

# Terms and conditions view
def terms_conditions(request):
    return render(request, 'accounts/terms_conditions.html')

# Signup review view
def signup_review(request):
    """ Review signup data before creating the user """
    signup_data = request.session.get('signup_data')
    print("Signup data:", signup_data)   # Remember to remove this debugging line 
    if not signup_data:
        return redirect('accounts:signup')
    
    # Convert data/time fields back to their original format if necessary
    if isinstance(signup_data.get('date_of_birth'), str):
        signup_data['date_of_birth'] = datetime.strptime(signup_data['date_of_birth'], '%Y-%m-%d').strftime('%Y-%m-%d')
    
    if isinstance(signup_data.get('preferred_time_from'), str):
        signup_data["preferred_time_from"] = datetime.strptime(signup_data['preferred_time_from'], '%H:%M:%S').strftime('%H:%M:%S')
    if isinstance(signup_data.get('prefered_time_to'), str):
        signup_data["preferred_time_to"] =  datetime.strftime(signup_data['preferred_time_to'], '%H:%M:%S').strftime('%H:%M:%S')
   

    if request.method == 'POST':
        form = CustomUserCreationForm(signup_data)  # User session data to populate form
        if form.is_valid():
            user = form.save(commit=False)
            user.verification_code = get_random_string(6, allowed_chars='0123456789')
            user.is_verified = True #Temporary 
            user.save()
            del request.session['signup_data']  # Clear session data after successful save

            # Send verification email
            #send_verification_email(request, user) Temporary 
            
            # Send SMS if phone number is provided
            #if user.email_or_phone.isdigit():        Temporary
            #    send_verification_sms(user.email_or_phone, user.verification_code).  Temporary

            messages.success(request, "Your account has been successfully created! You may now log in.")
            #return redirect('home')
            return redirect('accounts:login')
        #else:
        #    messages.error(request, "There was an error with your submission.")
        #    return redirect('accounts:signup')
            
    return render(request, 'accounts/signup_review.html', {'signup_data': signup_data})

def test_view(request):
    messages.success(request, "Test notification for debugging.") # remember to delete this block
    return render(request, 'account/signup.html')

# Profile view
@login_required
def profile(request, user_id):
    """
    View for logged-in user's profile.
    """
    #if not request.user.is_authenticated:
    #    return redirect('accounts:signup')
    try: 
        user_profile = UserProfile.objects.get(user__id=user_id)
        #user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        logger.errors("User profile does not found for the current user.")
        messages.error(request, "Profile not found.")
        return redirect("accounts:edit_profile")
    #user_profile = request.user.userprofile
    return render(request, 'accounts/profile.html', {'profile': user_profile})


# Send verification email view
#@login_required 
#def send_verification_email(request, user):
#   """
#    Send verification email to user's registered email adress or phone.
#    """
#    subject = 'Verify your email'
#    message = f'Your verification code is {user.verification_code}. Please use this code to verify your your account'
#    from_email = settings.DEFAULT_FORM_EMAIL
#    recipient_list = [user.email_or_phone] if "@" in user.email_confirm else []

#    if recipient_list:
#        send_mail(subject, message, from_email, recipient_list)
#        messages.success(request, 'A verification email has been sent. Please check your inbox.')

    # DELETE 
    #send_mail(subject, message, from_email, recipient_list)

    #messages.success(request, 'Verification email sent! Please check your inbox.')
    #return render(request, 'home')
    #return redirect('home')

    # DELETE

#def send_verification_sms(phone_number, verification_code):
#    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOCKEN)
#    client.message.create(
#        body=f'Your verification code is {verification_code}',
#        from_=settings.TWILIO_PHONE_NUMBER,
#        to=phone_number
#    )

# View for email confirmation
def email_confirm(request):
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        user = CustomUser.objects.filter(verification_code=code, is_verified=False).first()
        if user:
            user.is_verified = True
            user.verification_code = ''
            user.save()
            messages.success(request, 'Your account has been verified!')
            return redirect('home')
    else:
        messages.error(request, 'Invalid verification code. please try again.')

    return render(request, 'accounts/email_confirm.html')

# User login view

def login(request):
    """
    User login view using either email or phone
    """
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        logger.debug(f"Form data received: {request.POST}") # Debugging line

        #user = None
        if form.is_valid():
            logger.debug(f"Identifier: {form.cleaned_data['identifier']}, Password: {form.cleaned_data['password']}")
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            try:
                user = CustomUser.objects.get(email_or_phone=identifier)
            except CustomUser.DoesNotExist:
                logger.debug("User not found with identifier")  # Debugging line
                user = None
            
            if user:
            # Attempt to authenticate using custom field 
                user = authenticate(request, username=user.username, password=password)
                logger.debug (f"Login attempt with identifier: {identifier}") # Debugging line 
                if user is not None:
                    auth_login(request, user)
                    logger.debug(f"User authenticated sucessfully: {user.username}") # Debug
                    messages.success(request, 'Login Sussesful!')

                    # Redirect based on the user's role
                    if user.is_parent:
                        return redirect('accounts:parent_portal')
                    elif user.is_school_staff:
                        return redirect('accounts:school_portal')
                    else:
                        return redirect('home')
                    #return redirect('profile', user_id=user.id)
                    #return redirect('profile_view', user_id=user.id) # Redirect to home on sucessful login originally redirect('home')
                else:
                    logger.debug("Authentication failed. Invalid credentials") # Debug
                    messages.error(request, "Invalid login credentials. Please try agian.")
                    #form.add_error(None, "Invalid login credentials")
            else: 
                messages.error(request, "User not found with provided identifier") # Debugging line
        else:
            logger.debug(f"Form is in valid. Errors: {form.errors}") # Debug
            messages.error(request, "There was an error with your login information.")
        
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})    
    #return redirect('accounts:profile', {'form': form})
    #return redirect('profile', user_id=user.id)

# COMMENTED OUT TEMPORARILY 
# View to show a message when verification email is sent 
#def verification_sent(request):
#    return render(request, 'accounts/verification_sent.html')

# View for mail verification is required
def verified_email_required(request):
    return render(request, 'accounts/verified_email_required.html')

# Account inactive view
def account_inactive(request):
    return render(request, 'accounts/account_inactive.html')



# User profile list view
@login_required
def user_profile_list(request):
    profiles = UserProfile.objects.all()
    return render(request, 'accounts/profiles_list.html', {'profiles': profiles})

# User profile detail view
@login_required
def user_profile_details(request, pk):
    """
    User profile detail page for viewing individual profiles.
    """
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'accounts/user_profile_details.html', {'profile': profile})

# Edit profile view
@login_required
def edit_profile(request):
    """
    Allow users to edit profile information.
    """
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile') #  Redirect to profile detail view
        else:
            messages.error(request, "Error updating profile. Please check the form for errror.")
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

# Home view
#@login_required
def home(request):
    return render(request, 'home/home.html')

@login_required
def user_redirect_view(request):
    if request.user.is_parent:
        return redirect('parent_portal')
    elif request.user.is_school_staff:
        return redirect('school_portal')
    else:
        return redirect('home')

# Parent Portal View
@login_required
def parent_portal_view(request):
    return render(request, 'accounts/parent_portal.html')

# School Portal View
@login_required
def school_portal_view(request):
    return render(request, 'accounts/school_portal.html')

# About view
def about(request):
    return render(request, 'home/about.html')

# Contact view
def contact(request):
    return render(request, 'home/contact.html')