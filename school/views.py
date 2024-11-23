from django.shortcuts import render, redirect, get_object_or_404
from .forms import SchoolRegistrationForm, SchoolAccessForm
from .models import School
from django.contrib import messages



# Create your views here.

def school_registration(request):
    if request.method == "POST":
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            school = form.save(commit=False) # Save but dont commit to database yet
            request.session['school_data'] = form.cleaned_data
            return redirect('school:review')
    else:
        form = SchoolRegistrationForm()
    return render(request, 'school_registration.html', {'form': form})

# School Portal View
def school_review(request):
    school_data = request.session.get('school_data')
    if not school_data:
        return redirect('school:register')
    if request.method == "POST":
        # Save the school data to the database
        school = School.objects.create(**school_data)
        del request.session['school_data'] # Clear session data
        return redirect('school:portal', school_id=school.school_id)
    return render(request, 'school_review.html', {'school_data': school_data})

def school_portal(request, school_id):
    school = get_object_or_404(School, school_id=school_id)
    return render(request, 'school_access.html', {'school': school})


def school_access(request):
    if request.method == "POST":
        school = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            school = form.cleaned_data['school']
            full_name = form.cleaned_data['full_name']
            password = form.cleaned_data['password']
            # Redirect to the school's poertal with its ID
            return redirect('school:portal', school_id=school.school_id)
        else:
            messages.error(request, "Invalid details. Please try again.")
    else:
        form = SchoolAccessForm()
    return render(request, 'school_access.html', {'form': form})