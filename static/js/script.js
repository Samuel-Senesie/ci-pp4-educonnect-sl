// Toggle password visibility
function togglePasswordVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    field.type = field.type === "password" ? "text" : "password";
}

// Password strength checker
const passwordField = document.getElementById("id_password1");
const confirmPasswordField = document.getElementById("id_password2");
const strengthIndicator = document.getElementById("password_strength");
const suggestionBox = document.getElementById("password_suggestion");
const passwordMatchError = document.createElement("span");
passwordMatchError.className = "password_match_error";
passwordMatchError.style.color = "red";
passwordMatchError.style.fontSize = "0.5rem"
confirmPasswordField.parentNode.insertBefore(passwordMatchError, confirmPasswordField.nextSibling);
//const requiredFields = document.querySelectorAll("input[required]");

// Check password strength on input 
passwordField.addEventListener("input", function() {
    const password = this.value;
    const strength = checkPasswordStrength(password);

    if (password) {
        strengthIndicator.textContent = strength.message;
        strengthIndicator.className = `password_strength ${strength.class}`;
        if (strength.class === "weak") {
            displayPasswordSuggestion();
        } else {
            suggestionBox.style.display = "none";
        }
    } else {
        strengthIndicator.textContent = '';
        strengthIndicator.className = 'password_strength';
        suggestionBox.style.display = 'none';
    }

    clearPasswordFieldMismatchError();
});

// Real-time password match check
confirmPasswordField.addEventListener("input", function() {
    if (passwordField.value !== confirmPasswordField.value) {
        passwordMatchError.textContent = "Passwords do not match.";
        confirmPasswordField.classList.add("input-error");
    } else {
        passwordMatchError.textContent = "";
        confirmPasswordField.classList.remove("input-error");
    }
    clearPasswordFieldMismatchError();
});

function clearPasswordFieldMismatchError() {
    if(!passwordField.value || !confirmPasswordField.value) {
        passwordMatchError.textContent = "";
        confirmPasswordField.classList.remove('input_error');
    }
}

// Function to check password strength
function checkPasswordStrength(password) {
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    const mediumRegex = /^((?=.*[a-z])(?=.*[A-Z])|(?=.*[a-z])(?=.*\d)|(?=.*[A-Z])(?=.*\d)).{6,}$/;

    if (strongRegex.test(password)) {
        return { message: "Strong", class: "strong" };
    } else if (mediumRegex.test(password)) {
        return { message: "Medium", class: "medium" };
    } else {
        return { message: "Weak", class: "weak" };
    }
}

// Password suggestion display function
function displayPasswordSuggestion() {
    const suggestedPassword = generatePassword();
    suggestionBox.innerHTML = `Suggested Password: <span>${suggestedPassword}</span>`;
    suggestionBox.style.display = "block";
}

// Password generator for suggestions
function generatePassword() {
    const upperChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const lowerChars = "abcdefghijklmnopqrstuvwxyz";
    const numbers = "0123456789";
    const specialChars = "!@#$%^&*()_+";
    const allChars = upperChars + lowerChars + numbers + specialChars;
    let password = "";

    password += upperChars.charAt(Math.floor(Math.random() * upperChars.length));
    password += lowerChars.charAt(Math.floor(Math.random() * lowerChars.length));
    password += numbers.charAt(Math.floor(Math.random() * numbers.length));
    password += specialChars.charAt(Math.floor(Math.random() * specialChars.length));

    for (let i = 4; i < 12; i++) {
        password += allChars.charAt(Math.floor(Math.random() * allChars.length));
    }
    password = password.split('').sort(() => Math.random() - 0.5).join('');
    return password;
}

// Click on suggested password to replace user input
suggestionBox.addEventListener("click", function(event) {
    if (event.target.tagName === "SPAN") {
        passwordField.value = event.target.textContent;
        suggestionBox.style.display = "none";

        const strength = checkPasswordStrength(passwordField.value);
        strengthIndicator.textContent = strength.message;
        strengthIndicator.className = `password_strength ${strength.class}`;
    }
});

// Hide suggestion box on password field focus out
passwordField.addEventListener("blur", function() {
    setTimeout(() => { suggestionBox.style.display = "none"; }, 200);
});

// Highlighted required fields in red if they are emply on submit
document.querySelector("form").addEventListener("submit", function(event) {
    const requiredFields = [
        document.getElementById("id_first_name"),
        document.getElementById("id_last_name"),
        document.getElementById("id_email_or_phone"),
        document.getElementById("id_date_of_birth"),
        document.getElementById("id_gender"),
        document.getElementById("id_user_role"),
        document.getElementById("id_password1")
    ];

    let formIsValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            formIsValid = false;
            field.classList.add("input-error");

            field.addEventListener("input", function() {
                if (field.value.trim()) {
                    field.classList.remove("input-error");
                }
            });
        }
    });

    // Check if passwords match
    if (passwordField.value !== confirmPasswordField.value) {
        formIsValid = false;
        passwordMatchError = "Passwords do not match.";
        confirmPasswordField.classList.add("input-error")
    } else {
        passwordMatchError.textContent = "";
        confirmPasswordField.classList.remove("input-error");
    }

    if (!formIsValid) {
        event.preventDefault();
        alert("Please fill out all requred fields.")
    //} else {
    //    requiredFields.forEach(field => field.value = "");
    //    suggestionBox.style.display = "none";
    //    strengthIndicator.textContent = '';
    //    strengthIndicator.className = '';
    }

});

document.addEventListener("DOMContentLoaded", function() {
    const messageElements = document.querySelectorAll(".notification");
    if (messageElements.length > 0) {
        messageElements.forEach(function(message) {
            setTimeout(function() {
                message.classList.add('fade-out');
                setTimeout(function() {
                    message.style.display = 'none'
                }, 1000);  // Delay removal to allow fade-out effect
            }, 4000); // Start fade-out after 4 seconds
        });
    }
});

// Modal funtionality for User profile
const modal = document.getElementById("editProfileModal");
const editBtn = document.getElementById("editProfileBtn");
const closeBtn = document.getElementsByClassName("user-modal-close")[0];

editBtn.onclick = () => modal.style.display = "block";
closeBtn.onclick = () => modal.style.display = "none";
window.onclick = (event) => {
    if (event.target === modal) modal.style.display = "home"
};