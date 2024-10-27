from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    #path('about/', views.about, name='about'),
    #path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    #path('wlcome', views.welcome_view, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('signup/review/', views.signup_review, name='signup_review'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:pk>/', views.user_profile_details, name='user_profile_details'),

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/uibd64/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password change URLs/
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # Email verification URLs/
    path('email/', views.send_verification_email, name='send_verification_email'),
    path('email_confirm/', views.email_confirm, name='email_confirm'),
    path('verification_sent/', views.verification_sent, name='verification_sent'),
    path('verified_email_required/', views.verified_email_required, name='verified_email'),

    # Account activation and status URLs
    path('account_inactive/', views.account_inactive, name='account_inactive'),


    
]
