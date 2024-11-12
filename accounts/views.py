from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from .models import UserProfile, CustomUser
from .forms import CustomUserCreationForm, CustomLoginForm, UserProfileForm, ProfileEditForm
from datetime import date, time, datetime
from django.views.decorators.csrf import csrf_protect
from twilio.rest import Client
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, get_user_model
from django.urls import reverse
import logging 
from django.middleware.csrf import get_token
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.shortcuts import redirect

logger = logging.getLogger(__name__) #Debug

User = get_user_model()

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

    return render(request, 'signup.html', {'form': form})

# Terms and conditions view
def terms_conditions(request):
    return render(request, 'terms_conditions.html')

# Signup review view
def signup_review(request):
    """ Review signup data before creating the user """
    print("CSRF Token:", get_token(request))
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
            
    return render(request, 'signup_review.html', {'signup_data': signup_data})

def test_view(request):
    messages.success(request, "Test notification for debugging.") # remember to delete this block
    return render(request, 'account/signup.html')

# Profile view
@login_required
def profile(request):
    """
    View for logged-in user's profile.
    """
    #if not request.user.is_authenticated:
    #    return redirect('accounts:signup')
    try: 
        user_profile = get_object_or_404(UserProfile, user=request.user)
        #user_profile = UserProfile.objects.get(user__id=user_id)
        #user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        logger.errors("User profile does not found for the current user.")
        messages.error(request, "Profile not found.")
        return redirect("accounts:edit_profile")
    #user_profile = request.user.userprofile
    return render(request, 'profile.html', {'profile': user_profile})


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


# Custom Login View 
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    #@method_decorator(sensitive_post_parameters('password'))
    def form_valid(self, form):
        print("Is this method being called?")
        user = form.cleaned_data.get('user')
        # identifier = form.cleaned_data.get['identifier']
        # password = form.cleaned_data.get['password']

        identifier = form.cleaned_data.get('identifier')
        password = form.cleaned_data.get('password')


        logger.debug(f"Login attempt with identifier: {identifier}")

        # Retrive user based on identier
        try:
            user = CustomUser.objects.get(email_or_phone=identifier)
            logger.debug(f"User found: {user.username} ({user.user_role})")
        except CustomUser.DoesNotExist:
            logger.debug("User not found with the identifier.")
            form.add_error(None, "Invalid login credentials.")
            return self.form_invalid(form)
        
        #Authenticate the user with the retrieved user details
        #authenticated_user = authenticate(self.request, username=user.username, password=password)
        authenticated_user = self.authenticate_user(user, password)

        print("Authenticated User: ", authenticated_user)

        if authenticated_user:
            auth_login(self.request, authenticated_user)
            logger.debug(f"User authenticated successfully: {authenticated_user.username}")
            messages.success(self.request, 'Login successfully!')
            print("Should go to redirect method")
            return self.role_based_redirect(authenticated_user)
        else:
            logger.debug("Authentication failed. Invalid credentials.")
            messages.error(self.request, "Invalid login credentials.")
            return self.form_invalid(form)

    def authenticate_user(self, user, password):
        return authenticate(self.request, username=user.username, password=password)

    def role_based_redirect(self, user):
        print("Redirect by user_role: ", user.user_role)
            # Role-based redirection
        if user.user_role == 'Parent':
            logger.info(f"Redirecting {user.username} to the parent portal")
            return redirect('accounts:parent_portal')
        elif user.user_role == 'Teacher':
            logger.info(f"Redirecting {user.username} to the teacher portal")
            return redirect('accounts:teacher_portal')
        elif user.user_role == 'Administrator':
            logger.info(f"Redirecting {user.username} to the administrator portal")
            return redirec('accounts:administrator_portal')
        elif user.user_role == 'Police':
            logger.info(f"Redirecting {user.username} to the police portal")
            return redirect('accounts:police_portal')
        elif user.user_role == 'MCA':
            logger.info(f"Redirecting {user.username} to the MCA portal")
            return redirect('accounts:mca_portal')
        else:
            logger.info(f"No specific role matched for {user.username}. Redirecting to home.")
            return redirect('home')
    def form_invalid(self, form):
        print("Form errors:", form.errors)
        logger.warning("Form invalid. Login attempt failed due to invalid credentials.")
        return super().form_invalid(form)
 


# Logout view
def custom_logout_view(request):
    logout(request)
    return redirect('home')

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
def edit_profile(request, user_id):
    """
    Allow users to edit profile information.
    """
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile', user_id=user_id) #  Redirect to profile detail view
        else:
            messages.error(request, "Error updating profile. Please check the form for errror.")
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

# Delete profile view
def delete_profile(request):
    return render(request, 'accounts/delete_profile.html')

# Delete account view
def delete_account(request):
    return render(request, 'accounts/delete_account.html')

# Home view
@login_required
def home(request):
    return render(request, 'home.html')

# Parent Portal View
@login_required
def parent_portal_view(request):
    return render(request, 'parent_portal.html')

# School Portal View
@login_required
def school_portal_view(request):
    return render(request, 'school_portal.html')

# About view
def about(request):
    return render(request, 'home/about.html')

# Contact view
def contact(request):
    return render(request, 'home/contact.html')


# Password reset
def password_reset(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        user = None

        # Check if identifier is an email or a phone number
        if "@" in identifier:
            user = User.objects.filter(email=identifier).first()
            if user:
                # Send password reset email
                reset_link = request.build_absoulute_uri(
                    reverse("accounts:password_reset_verify", args=[user.pk])
                )
                send_mail(
                    "Password Reset Request",
                    f"Click the link to reset your password: {reset_link}",
                    "no-reply@yourdomain.com",
                    [user.email]
                )
                messages.success(request, "Password reset link has been sent to your email.")
                return redirect("accounts:login")
            else:
                messages.error(request, "No account found with that email.")
        else:
            user = User.objects.filter(phone_number=identifier).first()
            if user:
                # Generate and display verification code in the app
                verification_code = randint(100000, 999999)
                user.verification_code = verification_code
                user.save()
                messages.info(request, f"Your verification code is {verification_code}")
                return redirect("accounts:password_reset_verify")
            else:
                messages.error(request, "No account found with that phone number.")
    
    return render(request, "accounts/password_reset.html")


def password_reset_verify(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        verification_code = request.POST.get("code")
        new_password = request.POST.get("new_password")

        user = User.objects.filter(phone_number=identifier, verification_code=verification_code).first()
        if user:
            user.set_password(new_password)
            user.verification_code = None   # Clear verification code after use
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect("accounts:login")
        else:
            messages.error(request, "Invalid verification code or identifier.")
    return render(request, "accounts/password_reset_verify.html")