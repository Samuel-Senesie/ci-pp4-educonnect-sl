from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
#from django.http import HttpResponse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm, UserProfileForm
from datetime import date, time, datetime
from django.views.decorators.csrf import csrf_protect

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
            if 'date_of_birth' in cleaned_data and isinstance(cleaned_data['date_of_birth'], date):
                cleaned_data['date_of_birth'] = cleaned_data['date_of_birth'].isoformat()
            
            if 'preferred_time_from' in cleaned_data and isinstance(cleaned_data['preferred_time_from'], time):
                cleaned_data['preferred_time_from'] = cleaned_data['preferred_time_from'].isoformat()
            
            if 'preferred_time_to' in cleaned_data and isinstance(cleaned_data['preferred_time_to'], time):
                cleaned_data['preferred_time_to'] = cleaned_data['preferred_time_to'].isoformat()


            request.session['signup_data'] = cleaned_data  # Save the user
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
#@login_required
def signup_review(request):
    """ Review signup data before creating the user """
    signup_data = request.session.get('signup_data')
    print("Signup data:", signup_data)
    if not signup_data:
        return redirect('accounts:signup')
    # Convert date and time strings back to date and time objects
    #if 'date_of_birth' in signup_data:
        #signup_data['date_of_birth'] = datetime.strptime(signup_data['date_of_birth'], '%Y-%m-%d').date()
    if isinstance(signup_data.get('date_of_birth'), str):
        signup_data['date_of_birth'] = datetime.strptime(signup_data['date_of_birth'], '%Y-%m-%d').strftime('%Y-%m-%d')
    #if 'preferred_time_from' in signup_data:
        #signup_data['preferred_time_from'] = datetime.strptime(signup_data['preferred_time_from'], '%H:%M:%S').time()
    if isinstance(signup_data.get('preferred_time_from'), str):
        signup_data["preferred_time_from"] = datetime.strptime(signup_data['preferred_time_from'], '%H:%M').strftime('%H:%M')
    if isinstance(signup_data.get('prefered_time_to'), str):
        signup_data["preferred_time_to"] =  datetime.strftime(signup_data['preferred_time_to'], '%H:%M').strftime('%H:%M')
    #if 'preferred_time_to' in signup_data:
        #signup_data['preferred_time_to'] = datetime.strptime(signup_data['preferred_time_to'], '%H:%M:%S').time()

    if request.method == 'POST':
        form = CustomUserCreationForm(signup_data)  # User session data to populate form
        if form.is_valid():
            user = form.save()
            #backend = 'django.contrib.auth.backends.ModelBackend'
            #auth_login(request, user, backend=backend)
            del request.session['signup_data']  # Clear session data after successful save
            messages.success(request, "Account created successfully!")
            return redirect('home')
        #else:
        #    messages.error(request, "There was an error with your submission.")
        #    return redirect('accounts:signup')
            
    return render(request, 'accounts/signup_review.html', {'signup_data': signup_data})


# User login view
def login(request):
    """
    User login view using either emaiol or phone
    """
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            user = authenticate(request, username=identifier, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login Sussesful!')
                return redirect('home') # Redirect to home on sucessful log in
            else:
                messages.error(request, "Invalid login credentials. Please try agian.")
                #form.add_error(None, "Invalid login credentials")
        else:
            messages.error(request, "There was an error with your login information.")
        
    else:
        form = CustomLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})

# Profile view
@login_required
def profile(request):
    """
    View for logged-in user's profile.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:signup')
    user_profile = request.user.userprofile
    return render(request, 'accounts/profile.html', {'profile': user_profile})


# Send verification email view
@login_required
def send_verification_email(request):
    """
    Send verification email to user's registered email adress or phone.
    """
    subject = 'Verify your email'
    message = 'Click the link below to verify your email address.'
    from_email = settings.DEFAULT_FORM_EMAIL
    recipient_list = [request.user.email]

    send_mail(subject, message, from_email, recipient_list)

    messages.success(request, 'Verification email sent! Please check your inbox.')
    #return render(request, 'home')
    return redirect('home')

# View for email confirmation
def email_confirm(request):
    return render(request, 'accounts/email_confirm.html')

# View to show a message when verification email is sent 
def verification_sent(request):
    return render(request, 'accounts/verification_sent.html')

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
@login_required
def home(request):
    return render(request, 'home/home.html')

# About view
def about(request):
    return render(request, 'home/about.html')

# Contact view
def contact(request):
    return render(request, 'home/contact.html')