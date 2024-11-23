from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    path('school_access/', views.school_access, name='school_access'),
    path('register/', views.school_registration, name='register'),
    path('review/', views.school_review, name='review'),
    path('<uuid:school_id>/', views.school_portal, name='portal'),
]