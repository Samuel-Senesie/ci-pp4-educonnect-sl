from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, parent_portal_view, school_portal_view, custom_logout_view
from django.conf.urls.static import static
from django.conf import settings

app_name = 'accounts'

urlpatterns = [
    #path('home/', views.home, name='home'),
    path('login_view/', CustomLoginView.as_view(), name='login_view'),
    path('parent_portal/', views.parent_portal_view, name='parent_portal'),
    #path('teacher_portal/', views.teacher_portal_view, name='teacher_portal'),
    path('school_portal/', school_portal_view, name='school_portal'),
    path('signup/', views.signup, name='signup'),
    path('signup/review/', views.signup_review, name='signup_review'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/edit/<int:user_id>/', views.edit_profile, name='edit_profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('logout/', custom_logout_view, name='logout'),
    

    # Password reset URLs
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/uibd64/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password change URLs/
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # Email verification URLs/
    #path('email/', views.send_verification_email, name='send_verification_email'),
    path('email_confirm/', views.email_confirm, name='email_confirm'),
    #path('verification_sent/', views.verification_sent, name='verification_sent'),
    path('verified_email_required/', views.verified_email_required, name='verified_email'),

    # Account activation and status URLs
    path('account_inactive/', views.account_inactive, name='account_inactive'),
    path('accounts/', include('django.contrib.auth.urls'))
    
]
