from django.shortcuts import render, redirect, get_object_or_404
from .forms import SchoolRegistrationForm, SchoolAccessForm
from .models import School
from django.contrib import messages



# Create your views here.

def school_registration(request):
    # Retrive session data if it exists
    school_data = request.session.get('school_data', None)

    if request.method == "POST":
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            school = form.save(commit=False) # Save but dont commit to database yet
            # Save the data in the session for review
            request.session['school_data'] = form.cleaned_data
            return redirect('school:review') # Redirect to review page
    else:
        form = SchoolRegistrationForm(initial=school_data)
    return render(request, 'school_registration.html', {'form': form})

# School Portal View
def school_review(request):
    # Rertrieve school data from session
    school_data = request.session.get('school_data')
    if not school_data:
        # Redirect back to registration if session data is missing
        return redirect('school:register')
    
    if request.method == "POST":
        if 'edit' in request.POST:
            # Redirect back to registration form for editing 
            return redirect('school:register')
        
        if 'confirm' in request.POST:
        # Attempt to recreate the form with session data
            form = SchoolRegistrationForm(data=school_data)
            if form.is_valid():
                # Save the valid form to the database
                school = form.save()
                del request.session['school_data'] # Clear session data
                return redirect('school:portal', school_id=school.school_id)
            else:
                # Handle case where form data from session is invalid
                messages.error(request, "Invalid data in session. Please re.register")
                return redirect('school:register')
    return render(request, 'school_review.html', {'school_data': school_data})

# School Portal View
def school_portal(request, school_id):
    school = get_object_or_404(School, school_id=school_id)
    return render(request, 'school_access.html', {'school': school})

# School access portal 
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