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
from .forms import CustomUserCreationForm, CustomLoginForm, UserProfileForm, ProfileEditForm, UserProfileEditForm, CustomUserEditForm
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
from .forms import validate_and_resize_image
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

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
    #try: 
    user_profile = get_object_or_404(UserProfile, user=request.user)
    #except UserProfile.DoesNotExist:
    #    logger.errors("User profile does not found for the current user.")
    #    messages.error(request, "Profile not found.")
    #    return redirect("accounts:edit_profile", user_id=request.user.id)
    
    # Ensure default profile_picture is set is profile picture is missing
    if not user_profile.profile_picture or not user_profile.profile_picture.storage.exists(user_profile.profile_picture.name):
        user_profile.profile_picture = 'profile_pics/default_profile_pic.jpeg'
        user_profile.save()
    
    # # Ensure default background is set is profile picture is missing
    if not user_profile.background_image or not user_profile.background_image.storage.exists(user_profile.background_image.name):
        user_profile.background_image = 'background_images/default_background_image.jpeg'
        user_profile.save()


    if request.method == 'POST':
        # Handle profile picture and background image upload
        #profile_form = UserProfileEditForm(request.POST, request.FILES, isinstance=user_profile)
        #if profile_form.is_valid():
        #    profile_form.save()
        #    messages.success(request, 'Profile updated successfully!')

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('accounts:profile')
        
        # Handle background image upload
        elif 'background_image' in request.FILES:
            user_profile.background_image = request.FILES['background_image']
            user_profile.save()
            messages.success(request, 'Background image updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'No valid image upload found.')

            # Redirect users to their role-based views
    #        if request.user.user_role == "Parent":
    #            return redirect("accounts:parent_portal")
    #        elif request.user.user_role == "Teacher":
    #            return redirect("accounts:teacher_portal")
    #        else:
    #            return redirect ('home')
    #    else:
    #        messages.error(request, "Error updating profile image.")
    #else:
    #    profile_form = UserProfileEditForm(instance=user_profile)
    
    role_redirect_url = "home"
    if request.user.user_role == "Parent":
        role_redirect_url = "accounts:parent_portal"
    #elif request.user.user_role == "Teacher":
    #    role_redirect_url = "accounts:teacher_portal"

    return render(request, 'profile.html', {
        'profile': user_profile,
        #'profile_form': profile_form,
        'role_redirect_url': role_redirect_url,
    })

# Delete profile view
@login_required
def delete_profile(request):
    """ 
    Allows users to delete thier profile while keeping ther account active.
    """

    # First, try to fetch the UserProfile using .filter().first()
    user_profile = UserProfile.objects.filter(user=request.user).first()

    # if no profile exists, handle it grecefully 
    if not user_profile:
        messages.success(redirect, "No profile found to delete.")
        return redirect("home")
    
    # Use get_object_or_404 to provide fallback and prevent tamparing
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Handle profile deletion if user submits the form
    if request.method == "POST":
        # Delete the profile
        user_profile.delete()
        messages.success(request, "Your profile has been successfully deleted.")
        # Redirect to the home page or a relevan view
        return redirect ("home")

    # Render the confirmation page
    return render(request, "delete_profile.html", {"user_profile": user_profile})

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
#@login_required
#def edit_profile(request, user_id):
    """
    Allow users to edit profile information.
    """
#    user_profile = request.user.userprofile
#    if request.method == 'POST':
#        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
#        if form.is_valid():

             # Handle backgroun image and remove existing images if new ones are uploaded
#            background_image = form.cleaned_data.get('background_image')
#            if background_image:
#                resized_picture = validate_and_resize_image(background_image)
#                if user_profile.background_image:
#                    user_profile.background_image.delete(save=False)
#                user_profile.background_image.save(background_image.name, resized_picture)
                

            # Handle profile picture and remove existing images if new ones are uploaded
#            profile_picture = form.cleaned_data.get('profile_picture')
#            if profile_picture:
#                resized_picture = validate_and_resize_image(profile_picture)
#                if user_profile.profile_picture:
#                    user_profile.profile_picture.delete(save=False)
#                user_profile.profile_picture.save(profile_picture.name, resized_picture)      

            # Save changes
#            user_profile.save()
#            messages.success(request, 'Profile updated successfully!')
#            return redirect('accounts:profile') #  Redirect to profile detail view
#        else:
#            messages.error(request, "Error updating profile. Please check the form for errror.")
#    else:
#        form = UserProfileForm(instance=user_profile)
    
#    return render(request, 'edit_profile.html', {'form': form})

@login_required
def edit_profile(request, user_id):
    """
    View for editing user profile information.
    """
    #user = request.user
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        user_form = CustomUserEditForm(request.POST, instance=user)
        profile_form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)

        #Handle direct input of bio
        bio_data = request.POST.get('bio', '')
        if bio_data:
            user_profile.bio = bio_data # Save bio directly
    
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            user_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            print("User Form Errors:", user_form.errors)
            print("Profile Form Erros:", profile_form.errors)
            messages.error(request, "Error updating profile. Please check the form for errors")
    else:
        user_form = CustomUserEditForm(instance=user)
        profile_form = UserProfileEditForm(instance=user_profile)
    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'bio': user_profile.bio,
        'location': user_profile.location
    })




# Delete profile view
#def delete_profile(request):
#    return render(request, 'accounts/delete_profile.html')

# Delete account view
@login_required
def delete_account(request):
    """
    Allows users to delete their entire account, including the associated profile
    """
    user = request.user

    if request.method == "POST":
        # Delete the user's profile (if it exists)
        UserProfile.objects.filter(user=user).delete()

        # Delete the user's account
        user.delete

        # Log the user out after deleting thier account
        logout(request)

        messages.success(request, "Your account has been permanently deleted.")
        return redirect("home")
    
    return render(request, 'delete_account.html')

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